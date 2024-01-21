import numpy as np
import matplotlib.pyplot as plt
import random
import os
import argparse
from scipy.optimize import minimize

def segmented_function(params, x):
    a, b, c = params
    return np.minimum(1.4, a / (b * x + 0.488))

def objective_function(params, x, y, e_op):
    y_pred = segmented_function(params, x)
    y_pred[y_pred < 0.1] = 0.1
    weighted_error = e_op * np.sqrt((y - y_pred) ** 2) / y / y_pred
    return np.mean(weighted_error)

parser = argparse.ArgumentParser(description="node number")
parser.add_argument("dataset", type=str, help="dataset name")
parser.add_argument("node_num", type=np.int32, help="node number")
args = parser.parse_args()

NODE_NUM = args.node_num
DATASET_NAME = args.dataset
APPLY_TIME = 1.5
SLR_PER_NODE = 4
DUMMY_TASK = {'partition_id': str(0xffff), 'exe_time': 0.1} ## set the minimal time interval
RANDOM_NUM = 100
MAX_EXE_TIME = 0xffffffff
PATH = "./m_access/"
DRAW_PIC = True

class RangeSet:
    def __init__(self):
        self.ranges = []

    def add_range(self, min_val, max_val):
        if min_val <= max_val:
            self.ranges.append((min_val, max_val))
        else:
            raise ValueError("Invalid range: min_val is greater than max_val")

    def has_intersection(self, min_val, max_val):
        for r_min, r_max in self.ranges:
            if max(min_val, r_min) < min(max_val, r_max):
                return True
        return False

def getPartitionNum (dataset):
    ref_path = "/data/yufeng/single_4SLR_graph_dataset_bp2/" + dataset
    for p_idx in range(100):
        file_name = ref_path + "/p_" + str(p_idx) + "_sp_0.txt"
        if (os.path.exists(file_name) == False):
            return p_idx

##define optimal solution
workstations_opt = [[] for _ in range(NODE_NUM)] ## used for store partition id
exe_time_per_worker_opt = np.zeros(NODE_NUM, dtype=np.float64)

## load dataset hyper-parameter v/e + e + v
## Note that edge_op: edge access memory operation number
## Note that vertex_op: vertex access memory operation number
## Note that v_e_ratio: operation ratio

v_e_ratio = np.loadtxt(PATH + DATASET_NAME + "_v_e_ratio.txt")
edge_op = np.loadtxt(PATH + DATASET_NAME + "_e_op.txt")
vertex_op = np.loadtxt(PATH + DATASET_NAME + "_v_op.txt")
MTEPS_hw = np.loadtxt(PATH + DATASET_NAME + "_MTEPS.txt")

x = v_e_ratio
y = MTEPS_hw / 1000  # GTEPS
e_op_t = edge_op / max(edge_op)

initial_params = [0.9, 2, 1]
bounds = [(0, 1), (0.5, 7.8125), (None, None)]  # Bounds for a, b, and c

result = minimize(objective_function, initial_params, args=(x, y, e_op_t), bounds=bounds, method='L-BFGS-B')

if result.success:
    MTEPS = segmented_function(result.x, x) * 1000
else:
    print ("fitting failed, please change the bound range")
    exit(-1)

""" For version 1.0
var_op = np.loadtxt(PATH + DATASET_NAME + "_var.txt")
theta1 = 1350
theta2 = 100000
## estimate execution time for each partition
# V <= 0.192*E + 130686; MTEPS -> E
# V > 0.192*E + 130686; MTEPS -> E & V/E
"""

original_tasks = []
partitionNum = getPartitionNum(DATASET_NAME)

for p_idx in range(partitionNum):

    """ For version 1.0
    if (v_e_ratio[p_idx] <= 0.8):
    ## for small v/e
        MTEPS = 7809 / (2.8505 * v_e_ratio[p_idx] + (2480 / edge_op[p_idx]) + 3.0395) - 1012
        MTEPS = MTEPS * pow(theta1,2) / (pow((var_op[p_idx] + theta1), 2))
        MTEPS = np.array(MTEPS, dtype=np.int32)
        MTEPS[MTEPS > 1300] = 1300
    ## for large v/e
    else:
        MTEPS = 1396 / (2.375 * v_e_ratio[p_idx] - (6.5011 / edge_op[p_idx]) + 0.788) - 12.057 
        MTEPS = np.array(MTEPS, dtype=np.int32)
        MTEPS[MTEPS < 10] = 10.0
        MTEPS = MTEPS * pow(theta2,2) / (pow((var_op[p_idx] + theta2), 2))
    """
    exe_time = np.int32((edge_op[p_idx] * 8 / MTEPS[p_idx] / SLR_PER_NODE // 1000  + 1)) ## constant overhead
    original_tasks.append({"partition_id" : str(p_idx), "exe_time" : exe_time})

    """ Old method Version 0.0
    # if (vertex_op[p_idx] <= (0.192 * edge_op[p_idx] + 130686)):
    #     MTEPS = 1200 / ((4*1024*1024*0.0895 / edge_op[p_idx]) + 0.924)
    #     # MTEPS = 1300 / ((4*1024*1024*0.0895 / edge_op[p_idx]) + 0.924) * pow(theta1,2) / (pow((var_op[p_idx] + theta1), 2))
    # else:
    #     MTEPS = 1200 / (2.375 * v_e_ratio[p_idx] + (4*1024*1024*0.0155 / edge_op[p_idx]) + 0.468)
    #     MTEPS = 6.821 / (332.19 * v_e_ratio[p_idx] + (-1097724033 / edge_op[p_idx]) -4.047)
        ## * pow(theta2,2) / (pow((var_op[p_idx] + theta2), 2))
    # exe_time = np.int32((edge_op[p_idx] * 8 / MTEPS / SLR_PER_NODE // 1000  + 1)) ## constant overhead
    # print ("partition = ", p_idx, " MTEPS = ", MTEPS, " exe_time = ", exe_time)
    # original_tasks.append({"partition_id" : str(p_idx), "exe_time" : exe_time})
    """


## need to add a partition task split (for long execution time) to divide;
average_exe_time = 0
for p_idx in range(partitionNum):
    average_exe_time += original_tasks[p_idx]["exe_time"]
average_exe_time = (average_exe_time + NODE_NUM - 1) // NODE_NUM
# print ("average time = ", average_exe_time)
# print (original_tasks)

## used for example
# original_tasks = [{"partition_id" : 0, "exe_time" : 3},
#                   {"partition_id" : 1, "exe_time" : 5},
#                   {"partition_id" : 2, "exe_time" : 6},
#                   {"partition_id" : 3, "exe_time" : 4},
#                   {"partition_id" : 4, "exe_time" : 4},
#                   {"partition_id" : 5, "exe_time" : 8},
#                   {"partition_id" : 6, "exe_time" : 9},
#                   {"partition_id" : 7, "exe_time" : 2},
#                   {"partition_id" : 8, "exe_time" : 4}]

# task scheduler
# threshold = [i * 0.2 for i in range(int(2 / 0.2) + 1)]
threshold = [2]
for alpha in threshold:
    print ("parameter search .. threshold = ", alpha)
    thres_time = alpha * average_exe_time ## task exe time larger than thres_time, split;
    
    forward_tasks = [item for item in original_tasks if item["exe_time"] <= thres_time]
    all_reduce_tasks = [item for item in original_tasks if item["exe_time"] > thres_time]

    for R_IDX in range(RANDOM_NUM):
        
        workstations = [[] for _ in range(NODE_NUM)] ## used for store partition id
        exe_time_per_worker = np.zeros(NODE_NUM, dtype=np.float64)
        global_timestamp = RangeSet()
        
        ## all reduce tasks
        tasks_copy = all_reduce_tasks.copy()
        while tasks_copy:
            current_task = tasks_copy.pop(0)
            for node_idx in range(NODE_NUM):
                workstations[node_idx].append([current_task['partition_id'], (current_task['exe_time'] / NODE_NUM)])
                exe_time_per_worker[node_idx] = exe_time_per_worker[node_idx] + \
                                                (current_task['exe_time'] / NODE_NUM) + APPLY_TIME

        ## use random order
        random.shuffle(forward_tasks)
        ## use decending order
        ## forward_tasks = sorted(forward_tasks, key=lambda x: x['exe_time'], reverse=True)

        tasks = forward_tasks.copy()
        # print (tasks)

        while tasks:
            loop_length = len(tasks)
            change_flag = False
            for iteration in range(loop_length): ## loop once
                current_task = tasks.pop(0)
                ## print ("current task", current_task)
                work_id = np.argmin(exe_time_per_worker) ## get the min exe time workstation id

                range_lower = exe_time_per_worker[work_id] + current_task['exe_time']
                range_upper = range_lower + APPLY_TIME
                
                if (current_task['partition_id'] == str(0xffff)): ## dummy task, no need to check the time confliction
                    workstations[work_id].append([current_task['partition_id'], current_task['exe_time']])
                    exe_time_per_worker[work_id] = range_lower
                    change_flag = True
                    continue
                    # print ("assign DUMMY TASK into ", work_id)
                
                ## check whether the task can be assigned.
                if (global_timestamp.has_intersection(range_lower, range_upper)):
                    ## True, push the task to the bottom
                    tasks.append(current_task)
                else:
                    workstations[work_id].append([current_task['partition_id'], current_task['exe_time']])
                    global_timestamp.add_range(range_lower, range_upper)
                    exe_time_per_worker[work_id] = range_upper
                    change_flag = True
                    # print ("assign task: ", current_task['partition_id'], " into ", work_id)
                    
                    
            if (change_flag == False):
                # print ("task allocate failed, need to insert a DUMMY_TASK")
                tasks.append(DUMMY_TASK)

        ## pop the last DUMMY worker
        for node_id in range(NODE_NUM):
            if (len(workstations[node_id]) > 1):
                while (workstations[node_id][-1] == 0xffff):
                    # print ("delete dummy")
                    workstations[node_id].pop(-1)
                    exe_time_per_worker[node_id] -= 1
        
        ## check optimal solution
        current_time = max(exe_time_per_worker) ## need sync each super step
        if (current_time <= MAX_EXE_TIME):
            workstations_opt = workstations
            exe_time_per_worker_opt = exe_time_per_worker
            MAX_EXE_TIME = current_time

print ("Name ", DATASET_NAME, " scheduler, Node number = ", NODE_NUM, " max_time = ", MAX_EXE_TIME)
for n_idx in range(NODE_NUM):
    print ("Node ", n_idx, " exe_time = ", exe_time_per_worker_opt[n_idx], " task order : ", workstations_opt[n_idx])
workstations_opt = [[item for item in sublist if item != ['65535', 2]] for sublist in workstations_opt]
print (workstations_opt)

workstations_opt_filter = [[item for item in sublist if item[0] != '65535'] for sublist in workstations_opt]
print (workstations_opt_filter)

output_file = "schedule.txt"
with open(output_file, "w") as file:
    for sublist in workstations_opt_filter:
        file.write("PartitionList: ")
        file.write(" ".join(entry[0] for entry in sublist))
        file.write("\n")
# print("All partitions have been assigned.")

## draw the task execution timeline
if DRAW_PIC == True:

    figure_length = max(len(sublist) for sublist in workstations_opt) + 4
    fig, ax = plt.subplots(figsize=(figure_length, NODE_NUM * 2))  # Adjust the figure size based on the number of machines

    # Plot tasks for each machine
    for machine_index in range(NODE_NUM):
        timeline = 0
        for task_index in range(len(workstations_opt[machine_index])):
            p_id = workstations_opt[machine_index][task_index] ## partition id
            if (p_id[0] == str(0xffff)):
                ## DUMMY TASK
                color = 'Orange'
                task_time = DUMMY_TASK['exe_time'] ## dummy task time
                end_point = timeline + task_time
                ax.plot([timeline, end_point], [machine_index, machine_index], color=color, linewidth=30, solid_capstyle='butt')
                
                mid_time = timeline + (end_point - timeline) / 2
                text_color = 'black' if color == '#FFFFFF' else 'white'
                ax.text(mid_time, machine_index, 'D', color=text_color, verticalalignment='center', horizontalalignment='center')
                
                timeline = end_point
                
            else:
                ## GS task, bug: all-reduce task plot a little bit long
                color = 'grey'
                task_time = p_id[1]
                # task_time = [task['exe_time'] for task in original_tasks if task['partition_id'] == p_id][0]
                end_point = timeline + task_time
                ax.plot([timeline, end_point], [machine_index, machine_index], color=color, linewidth=30, solid_capstyle='butt')

                mid_time = timeline + (end_point - timeline) / 2
                text_color = 'black' if color == '#FFFFFF' else 'white'
                ax.text(mid_time, machine_index, str(p_id[0]), color=text_color, verticalalignment='center', horizontalalignment='center')
                
                ## APPLY task
                color = 'lightblue'
                timeline = end_point
                end_point = timeline + APPLY_TIME
                ax.plot([timeline, end_point], [machine_index, machine_index], color=color, linewidth=30, solid_capstyle='butt')
                
                mid_time = timeline + (end_point - timeline) / 2
                text_color = 'black' if color == '#FFFFFF' else 'white'
                ax.text(mid_time, machine_index, 'A', color=text_color, verticalalignment='center', horizontalalignment='center')
                
                timeline = end_point

    ax.set_yticks(range(NODE_NUM))
    ax.set_yticklabels([str(machine_id) for machine_id in range(NODE_NUM)])
    ax.set_ylim(-1, NODE_NUM)
    ax.set_title('Task Timeline for Machines')
    plt.tight_layout()

    # Save the figure to a PNG file
    plt.savefig("machine_task_timeline_" + DATASET_NAME + ".png", dpi=300)

