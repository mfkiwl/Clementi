import re

# Load the data from files
def load_data(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    return lines

# Extract data considering the observed format
def extract_data(lines):
    data = {}
    current_graph = None
    # Regular expression pattern for partition and time extraction
    pattern = re.compile(r'\[(\d+)\] +device +time += +(\d+)')
    for line in lines:
        # Check if the line contains the graph name
        if "run" in line:
            current_graph = line.split()[1].strip()
            data[current_graph] = {}
        # Check if the line contains the partition time
        elif "[" in line:
            partition, time = pattern.findall(line)[0]
            data[current_graph][partition] = int(time)
    return data

# Calculate simulation error ratio
def calculate_error(hw_time, sim_time):
    return abs((sim_time - hw_time) / hw_time) * 100

# Calculate error ratio for each partition and average error for each graph
def calculate_error_ratios(hw_perf_data, simulation_data, graph_names):
    error_data = {graph: {} for graph in graph_names}
    for graph in graph_names:
        total_error = 0
        total_hw = 0
        total_pred = 0
    
        hw_times = hw_perf_data.get(graph, {})
        sim_times = simulation_data.get(graph, {})
        partition_errors = []
        
        # Check if the graph is present in both datasets
        if hw_times and sim_times:
            common_partitions = set(hw_times.keys()).intersection(sim_times.keys())
            
            # Calculate error for each partition
            for partition in common_partitions:
                error = calculate_error(hw_times[partition], sim_times[partition])
                partition_errors.append(error)
                error_data[graph][partition] = error
                total_hw = total_hw + hw_times[partition]
                total_pred = total_pred + sim_times[partition]
                total_error = total_error + abs(hw_times[partition] - sim_times[partition])
            
            # Calculate and store average error for the entire graph
            # error_data[graph]['average'] = sum(partition_errors) / len(partition_errors)
            error_data[graph]['average'] = (total_error / total_hw) * 100
            ratio_pred_hw = abs(total_pred - total_hw) / total_hw * 100
            print ("Name = ", graph," total_pred = ", total_pred, " total_hw = ", total_hw, " error_ratio = ", ratio_pred_hw)
    return error_data

# Load data from files
hw_perf_lines = load_data("./hw_perf.log")
simulation_lines = load_data("./simulation.log")

# Extract data from the files
hw_perf_data = extract_data(hw_perf_lines)
simulation_data = extract_data(simulation_lines)

# Specify graph names
graph_names = ['R21', 'G23', 'HW', 'WP', 'LJ', 'R24', 'G24', 'G25', "TW", "Friendster"]

# Calculate error ratios
error_data = calculate_error_ratios(hw_perf_data, simulation_data, graph_names)

# Display error data
for graph, partitions in error_data.items():
    print(f"\nError Ratios for {graph}:")
    for partition, error in partitions.items():
        if partition == 'average':
            print(f"  Average Error: {error:.2f}%")
        else:
            print(f"  Partition {partition}: {error:.2f}%")

