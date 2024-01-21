import numpy as np
import multiprocessing
import sys
import os
import psutil

BURST_LENGTH = 32
Granularity = 16

base_path = "/data/yufeng/single_4SLR_graph_dataset_bp2/"  # Replace with the actual file path
base_sub_partition = 4
# dataset_name = ["R25", "G24", "G25", "TW", "Friendster", "GSH", "SK", "UK2007-05", "K28-32"] ## for large real graph processing
dataset_name = ["G23", "HW", "LJ", "R24", "WK", "WP"]

# Function to read a binary file and return its contents as a NumPy array
def read_binary_file(filename):
    with open(filename, 'rb') as file:
        data = np.fromfile(file, dtype=np.int32)
        data = data.reshape(-1, 2)
        data = data[(data[:, 1] != -2)][1:]
    return data

def calculate_remainders(chunk):
    dest_vertices = chunk[:, 1]  # dest vertex in second column
    remainders = dest_vertices % 16
    return np.bincount(remainders, minlength=16)

for dataset in dataset_name:

    file_path = base_path + dataset
    partition_num = 0
    for p in range(100):
        ck_file_name = file_path + "/p_" + str(p) + "_sp_0.bin"
        if os.path.exists(ck_file_name):
            partition_num = p + 1
    print ("dataset = ", dataset, " partition_num = ", partition_num)
    scale_num = np.zeros((partition_num), dtype=np.float64)
    
    for partition in range(partition_num):
        file_names = []
        for sp_idx in range(base_sub_partition):
            file_names.append(base_path + dataset + "/p_" + str(partition) + "_sp_" + str(sp_idx) + ".bin")
            
        # Create a multiprocessing Pool with base_sub_partition processes
        with multiprocessing.Pool(processes=base_sub_partition) as pool:
            # Use pool.map to read each binary file with a specific process
            arrays = pool.map(read_binary_file, file_names)
        
        edgelist = np.concatenate(arrays, axis=0)
        arrays = [] ## release memory.
        
        num_processes = 64
        chunk_size = len(edgelist) // num_processes
        chunks = [edgelist[i:i + chunk_size] for i in range(0, len(edgelist), chunk_size)]

        with multiprocessing.Pool(num_processes) as pool:
            results = pool.map(calculate_remainders, chunks)

        total_counts = np.sum(results, axis=0)
        mean_value = np.mean(total_counts)
        max_value = np.max(total_counts)
        min_value = np.min(total_counts)
        scale_num[partition] = np.float64(max_value/mean_value)
        print ('partition id = ', partition)
        print (total_counts)
        print ('max = ', max_value, ' min = ', min_value, ' mean = ', mean_value)
        print ('max = ', max_value/np.sum(total_counts), ' min = ', min_value/np.sum(total_counts), ' mean = ', mean_value/np.sum(total_counts))
    
    np.savetxt("./m_access/" + dataset + "_scale.txt", scale_num, delimiter=' ')
        
