## need to add remap to balance edge number in different partition, and then balance the edge and vertex number in each subpartition.

import numpy as np
import sys
import os

SUB_PARTITION_NUM = 16
PARTITION_SIZE = 1024*1024

base_path = "/data/yufeng/single_4SLR_graph_dataset/"  # Replace with the actual file path
sub_partition_base = 4 ## if use 4node_4SLR, should be 16
dataset_name = ["G25", "UK2007-05"] ## for large real graph processing

storage_path = "/data/yufeng/4node_4SLR_graph_dataset_bp_remap/"

for dataset in dataset_name:

    file_path = base_path + dataset
    partition_num = 0
    for p in range(100):
        ck_file_name = file_path + "/p_" + str(p) + "_sp_0.bin"
        if os.path.exists(ck_file_name):
            partition_num = p + 1
    print ("dataset = ", dataset, " partition_num = ", partition_num)
    
    s_path = storage_path + dataset
    if (os.path.exists(s_path) == True):
        print("Already exists ", s_path)
        continue
    else :
        os.mkdir(s_path)
        print("Create directory ", s_path)

    edge_array = np.empty((0,2), dtype=np.int32)
    for partition in range(partition_num):
        for sp in range(sub_partition_base):
            file_name = base_path + dataset + "/p_" + str(partition) + "_sp_" + str(sp) + ".txt"
            print ("read file ", file_name, end=" ")
            edge_t = np.loadtxt(file_name, dtype=np.int32)
            edge_t = edge_t[(edge_t[:, 1] != -2)][1:]
            edge_array = np.vstack((edge_array, edge_t))
            print (" length = ", len(edge_array))
    
    # if (dataset == "Friendster"):
    #     file_name = "/data/graph_dataset/out.friendster"
    # elif (dataset == "UK2007-05"):
    #     file_name = "/data/graph_dataset/out.dimacs10-uk-2007-05"
    
    # print ("reading edge list into numpy, dataset = ", file_name)
    # edge_array = np.loadtxt(file_name, dtype=np.int32)
    # print ("original dataset = ", file_name, " edge_num = ", len(edge_array), " vertex num = ", np.max(edge_array) + 1)
    # print ("delete edge which contains 0 outdegree vertex, dataset = ", file_name)
    # outdeg = np.bincount(edge_array[:, 0], minlength = np.max(edge_array) + 1)
    # edges_to_remove = np.logical_or(outdeg[edge_array[:, 0]] == 0, outdeg[edge_array[:, 1]] == 0)
    # edge_array = edge_array[~edges_to_remove]
    # print ("after filter dataset = ", file_name, " edge_num = ", len(edge_array), " vertex num = ", np.max(edge_array) + 1)
    # print ("load edge list finish, sorting, dataset = ", file_name)
    # src_indices = np.argsort(edge_array[:, 0])
    # edge_array = edge_array[src_indices]

    ## already finish sort: ascending order. ## important
    vertex_num = edge_array.max() + 1
    print ("vertex num = ", vertex_num)
    
    ## finish read original dataset.
    dest_vertices = edge_array[:, 1]
    
    partition_num = np.int32(((dest_vertices.max() + 1) + PARTITION_SIZE - 1) // PARTITION_SIZE)
    print ("dataset :", dataset, " partition num = ", partition_num)
    
    if (vertex_num >= (PARTITION_SIZE * partition_num)):
        remap_size = vertex_num
    else:
        remap_size = PARTITION_SIZE * partition_num
    
    indegree_distribution = np.bincount(dest_vertices, minlength=remap_size)
    sorted_indices = np.argsort(indegree_distribution)[::-1]
    indegree_distribution = indegree_distribution[sorted_indices]
    print (sorted_indices)
    print (indegree_distribution)
    
    ## put edge data into different partitions.
    combined_list = list(zip(sorted_indices, indegree_distribution))
    groups = [[] for _ in range(partition_num)]
    group_sum = [0] * partition_num

    remap_nodes = PARTITION_SIZE * partition_num ## important！

    for start in range(0, remap_nodes, partition_num):
        group_sort_indices = np.argsort(group_sum)
        end = start + partition_num
        nodes_to_assign = combined_list[start:end]
        
        for idx, item in enumerate(nodes_to_assign):
            groups[group_sort_indices[idx]].append(item[0])
            group_sum[group_sort_indices[idx]] += item[1]
    
    group_sort_indices = np.argsort(group_sum)
    print ("vertex allocated to each partition, edge num = ", group_sum)
    
    ## create REMAP_ARRAY, (mapped id to original id).
    
    REMAP_ARRAY = np.zeros((remap_size, 2), dtype = np.int32)
    map_idx = 0
    for g in range(len(groups)):
        for m in range(PARTITION_SIZE):
            REMAP_ARRAY[map_idx][0] = map_idx
            REMAP_ARRAY[map_idx][1] = groups[g][m]
            map_idx = map_idx + 1

    if (vertex_num >= remap_nodes):
        nodes_to_assign = combined_list[remap_nodes:vertex_num] ## for the remaining edge list.
        for idx, item in enumerate(nodes_to_assign):
            REMAP_ARRAY[map_idx][0] = map_idx
            REMAP_ARRAY[map_idx][1] = item[0]
            map_idx = map_idx + 1
    
    # print ("remapped array = ", REMAP_ARRAY)
    np.savetxt(s_path + "/remap_idx.txt", REMAP_ARRAY[:, 1], fmt='%d', delimiter=' ')
    idx_remap = REMAP_ARRAY[REMAP_ARRAY[:, 1].argsort()]
    idx_remap = idx_remap[:, 0]
    np.savetxt(s_path + "/idx_remap.txt", idx_remap, fmt='%d', delimiter=' ')

    ## edge list remapping
    print ("processing edge list remapping ... ")
    remap_edge = np.zeros((len(edge_array), 2), dtype = np.int32)
    for e in range(len(edge_array)):
        remap_edge[e][0] = idx_remap[edge_array[e][0]]
        remap_edge[e][1] = idx_remap[edge_array[e][1]]
    
    sorted_dst = np.argsort(remap_edge[:, 1])
    remap_edge = remap_edge[sorted_dst]
    print ("remapped edge len = ", len(remap_edge), " edge list = ", remap_edge)
    np.savetxt(s_path + "/remap_edge_sort_dest.txt", remap_edge, fmt='%d', delimiter=' ')

    p_idx = [0] + group_sum
    p_idx = np.cumsum(p_idx)
    print ("index of remapped edge list", p_idx)
    for p in range(partition_num):
        print ("range = ", p_idx[p], " : ", p_idx[p+1])
        partial_graph = remap_edge[p_idx[p]:p_idx[p+1], :]
        sorted_src = np.argsort(partial_graph[:, 0])
        partial_graph = partial_graph[sorted_src]
        np.savetxt(s_path + "/remap_edge_" + str(p) + ".txt", partial_graph, fmt='%d', delimiter=' ')
    print ("save remapped array done")
    
    