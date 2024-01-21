import numpy as np
import multiprocessing
import sys
import os
import psutil

base_path = "/data/yufeng/4node_4SLR_graph_dataset/"  # Replace with the actual file path
base_sub_partition = 16
# dataset_name = ["G25", "Friendster", "TW", "UK2007-05"] ## for large real graph processing
dataset_name = ["UK2007-05"]
SUB_PARTITION_NUM = [1, 4, 8, 16, 32, 64]
PARTITION_SIZE = 1024 * 1024
BURST_LENGTH = 32
Granularity = 16

# Function to read a binary file and return its contents as a NumPy array
def read_binary_file(filename):
    with open(filename, 'rb') as file:
        data = np.fromfile(file, dtype=np.int32)
        data = data.reshape(-1, 2)
        data = data[(data[:, 1] != -2)][1:]
    return data

# Example function to process a chunk of the edge list and return three values
def process_chunk(chunk):
        
    edge_len = len(chunk)
    vertex_mem_access_number_512 = 0 ## 512 bit width memory access number
    last_item = -1

    for i in range(0, edge_len, Granularity):
        batch_edges = chunk[i:i+Granularity]
        batch_sources = batch_edges[:, 0]  # Extract source vertices from batch
        
        batch_sources //= (Granularity * BURST_LENGTH) ## coalescing and merge
        unique_values = np.unique(batch_sources) ## merge same item

        for ele in unique_values:
            if (last_item != ele):
                vertex_mem_access_number_512 += (1 * BURST_LENGTH) ## caculate the memory operation
                last_item = ele
    
    v_op_num = vertex_mem_access_number_512
    e_op_num = (edge_len // Granularity * 2)
    print (v_op_num, e_op_num)
    
    if (v_op_num <= (0.192 * e_op_num + 130686)):
        MTEPS = 1200 / ((4*1024*1024*0.0895 / e_op_num) + 0.924)
    else:
        MTEPS = 1200 / (2.375 * v_op_num / e_op_num + (4*1024*1024*0.0155 / e_op_num) + 0.468)
    exe_time = np.int32(e_op_num * 8 / MTEPS // 1000)  ## each edge mem operation has 8 edges, ms

    return exe_time


for dataset in dataset_name:
    print ("dataset = ", dataset)
    
    file_path = base_path + dataset
    partition_num = 0
    for p in range(100):
        ck_file_name = file_path + "/p_" + str(p) + "_sp_0.bin"
        if os.path.exists(ck_file_name):
            partition_num = p + 1
    print ("dataset = ", dataset, " partition_num = ", partition_num)
    
    for partition in range(partition_num):

        file_names = []
        for sp_idx in range(base_sub_partition):
            file_names.append(base_path + dataset + "/p_" + str(partition) + "_sp_" + str(sp_idx) + ".bin")
            
        # Create a multiprocessing Pool with base_sub_partition processes
        with multiprocessing.Pool(processes=base_sub_partition) as pool:
            # Use pool.map to read each binary file with a specific process
            arrays = pool.map(read_binary_file, file_names)
        
        edge_list = np.concatenate(arrays, axis=0)
        arrays = [] ## release memory.
        
        for sp_size in SUB_PARTITION_NUM:
            
            num_processes = sp_size
            chunk_size = len(edge_list) // num_processes
            chunks = [edge_list[i:i + chunk_size] for i in range(0, len(edge_list), chunk_size)]
            # If the last chunk is smaller than the rest, merge it with the previous chunk
            if len(chunks[-1]) < chunk_size and len(chunks) > 1:
                chunks[-2] = np.vstack((chunks[-2], chunks[-1]))
                chunks.pop()  # Remove the last (now empty) chunk

            with multiprocessing.Pool(processes=num_processes) as pool:
                # Use the map() method to apply the process_chunk function to each chunk
                results = pool.map(process_chunk, chunks)

            # Unpack the results
            results = np.array(results)
            
            # Print the combined results
            print("Dataset ", dataset, " partition_id ", partition, " sub_partition ", sp_size, "exe_time = ", np.max(results))

            