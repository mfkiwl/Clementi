import numpy as np
from multiprocessing import Pool
import sys
import os
import psutil

BURST_LENGTH = 32
Granularity = 16

base_path = "/data/yufeng/single_4SLR_graph_dataset_bp2/"  # Replace with the actual file path
base_sub_partition = 4
# dataset_name = ["GSH", "SK", "G24", "UK2007-05", "R25", "G25", "TW", "Friendster", "K28-32"] ## for large real graph processing
# dataset_name = ["R25-2-0", "R25-2-1", "R25-2-2", "R25-2-3",
#                 "R25-4-0", "R25-4-1", "R25-4-2", "R25-4-3",
#                 "R25-8-0", "R25-8-1", "R25-8-2", "R25-8-3",
#                 "R25-16-0", "R25-16-1", "R25-16-2", "R25-16-3",
#                 "R25-32-0", "R25-32-1", "R25-32-2", "R25-32-3",
#                 "R25-64-0", "R25-64-1", "R25-64-2", "R25-64-3"] ## for large real graph processing
dataset_name = ["WK"] ## for large real graph processing

# Function to read a binary file and return its contents as a NumPy array
def read_binary_file(filename):
    with open(filename, 'rb') as file:
        data = np.fromfile(file, dtype=np.int32)
        data = data.reshape(-1, 2)
        data = data[(data[:, 1] != -2)][1:]
    return data

def count_elements_in_block(args):
    arr, block_min, block_max = args
    count = np.sum((arr >= block_min) & (arr < block_max))
    return count

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
        with Pool(processes=base_sub_partition) as pool:
            # Use pool.map to read each binary file with a specific process
            arrays = pool.map(read_binary_file, file_names)
        
        edgelist = np.concatenate(arrays, axis=0)
        arrays = [] ## release memory.
        
        num_processes = 64
        arr = edgelist[:,0]
        print (arr)

        """Parallel process the array and count elements in each chunk, ensuring consistency."""
        max_value = np.max(arr)
        num_blocks = 16
        block_size = max_value / num_blocks
        pool = Pool(64) ## 64 processors
        block_ranges = [(arr, i*block_size, min((i+1)*block_size, max_value + 1)) for i in range(num_blocks)]
        counts = pool.map(count_elements_in_block, block_ranges)
        pool.close()
        pool.join()
        percentages = (np.array(counts) / len(arr)) * 100
        variance = np.var(percentages)
        print (percentages, variance)
        scale_num[partition] = variance
        
    np.savetxt("./m_access/" + dataset + "_var.txt", scale_num, delimiter=' ')
        
