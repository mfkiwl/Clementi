import numpy as np
import multiprocessing
import sys
import os
import psutil

bur_len = 32
Granularity = 16 ## each burst operation reads 16 vertex.

base_path = "/data/yufeng/single_4SLR_graph_dataset_bp2/"  # Replace with the actual file path
SUB_PARTITION_NUM = 4
# dataset_name = ["WP", "LJ", "G25", "Friendster", "TW", "UK2007-05"] ## for large real graph processing
dataset_name = ["WK"] ## for large real graph processing

# Function to read a binary file and return its contents as a NumPy array
def read_binary_file(filename):
    with open(filename, 'rb') as file:
        data = np.fromfile(file, dtype=np.int32)
        data = data.reshape(-1, 2)
        data = data[(data[:, 1] != -2)][1:]
    return data


for dataset in dataset_name:

    file_path = base_path + dataset
    partition_num = 0
    for p in range(100):
        ck_file_name = file_path + "/p_" + str(p) + "_sp_0.bin"
        if os.path.exists(ck_file_name):
            partition_num = p + 1
    print ("dataset = ", dataset, " partition_num = ", partition_num)
    
    v_mem_num = np.zeros((partition_num), dtype = np.int32)
    e_mem_num = np.zeros((partition_num), dtype = np.int32)
    v_e_mem_ratio = np.zeros((partition_num), dtype = np.float64)
    dst_congest_ratio = np.zeros((partition_num), dtype = np.float64) ## store the dst impact number

    ## estimate each partition execution time through its V/E memory access number and Edge number;
    for partition in range(partition_num):
        print ("process partition ", partition)

        file_names = []
        for sp_idx in range(SUB_PARTITION_NUM):
            file_names.append(base_path + dataset + "/p_" + str(partition) + "_sp_" + str(sp_idx) + ".bin")
            
        # Create a multiprocessing Pool with SUB_PARTITION_NUM processes
        with multiprocessing.Pool(processes=SUB_PARTITION_NUM) as pool:
            # Use pool.map to read each binary file with a specific process
            arrays = pool.map(read_binary_file, file_names)
        
        edge_array = np.concatenate(arrays, axis=0)
        arrays = [] ## release memory.
        
        last_item = -1
        v_mem_number = 0
        dst_congest_num = 0
        
        for i in range(0, len(edge_array), Granularity):
            batch_edges = edge_array[i:i+Granularity]
            batch_sources = batch_edges[:, 0]  # Extract source vertices from batch
            batch_dest = batch_edges[:, 1]  # Extract dest vertices from batch
            
            batch_sources //= (Granularity * bur_len) ## coalescing and merge
            unique_values = np.unique(batch_sources) ## merge same item
            
            batch_dest = batch_dest % 16 ## 16 shuffle PEs
            dest_values, dst_counts = np.unique(batch_dest, return_counts=True)
            
            ## original 2 cycles -> 16 edges
            ## congestion (dst_congest_num-1)*2 cycle2 -> 16 edges
            dst_congest_num += np.max(dst_counts)

            for ele in unique_values:
                if (last_item != ele):
                    v_mem_number += bur_len
                    last_item = ele
        
        v_mem_num[partition] = v_mem_number
        e_mem_num[partition] = (len(edge_array) + 7) // 8
        v_e_mem_ratio[partition] = "{:.2f}".format((v_mem_number / ((len(edge_array) + 7) // 8)))
        dst_congest_ratio[partition] = "{:.2f}".format(dst_congest_num / (len(edge_array) // Granularity))
        
    print ("v_mem_num = ", v_mem_num)
    print ("e_mem_num = ", e_mem_num)
    print ("v_e_mem_ratio = ", v_e_mem_ratio)
    print ("dst_congest_ratio = ", dst_congest_ratio)
    
    

        

        