import numpy as np
import sys
import os

SUB_PARTITION_NUM = 16
burst_len = 32
burst_vertex_num = burst_len * 16  ## 16 = 512 bit / 32 bit

base_path = "/data/yufeng/4node_4SLR_graph_dataset/"  # Replace with the actual file path
dataset_name = ["Friendster", "TW", "UK2007-05"] ## for large real graph processing

storage_path = "/data/yufeng/4node_4SLR_graph_dataset_bp/"

for dataset in dataset_name:
    file_path = base_path + dataset
    partition_num = 0
    for p in range(100):
        ck_file_name = file_path + "/p_" + str(p) + "_sp_15.bin"
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
        
    for partition in range(partition_num):
        
        edge_array = np.empty((0,2), dtype=np.int32)
        for sp in range(SUB_PARTITION_NUM):
            file_name = base_path + dataset + "/p_" + str(partition) + "_sp_" + str(sp) + ".txt"
            print ("read file ", file_name)
            edge_t = np.loadtxt(file_name, dtype=np.int32)
            edge_t = edge_t[(edge_t[:, 1] != -2)][1:]
            edge_array = np.vstack((edge_array, edge_t))
            print (edge_array, " length = ", len(edge_array))
        
        ## already finish sort: ascending order. ## important
        vertex_num = edge_array.max() + 1
        print (vertex_num)



        source_nodes = edge_array[:, 0].copy()
        source_nodes //= burst_vertex_num
        source_nodes = np.array(source_nodes, dtype = np.int32)

        print (source_nodes)

        max_group_id = np.max(source_nodes)
        group_edge_num = np.bincount(source_nodes, minlength=max_group_id+1)
        accumulated_group = np.cumsum(group_edge_num)
        group_index = np.insert(accumulated_group, 0, 0)
        print (group_index)

        unique_elements, outdegree = np.unique(source_nodes, return_counts=True)

        ## sort the source vertex of subgraph by indegree in a decending order
        sorted_indices = np.argsort(outdegree)[::-1]
        sorted_out_degree_values = outdegree[sorted_indices]
        sorted_node_ids = unique_elements[sorted_indices]


        combined_list = list(zip(sorted_node_ids, sorted_out_degree_values))
        groups = [[] for _ in range(SUB_PARTITION_NUM)]
        groups_outdegree = [[] for _ in range(SUB_PARTITION_NUM)]
        group_sum = [0] * SUB_PARTITION_NUM

        ## divide the group by SUB_PARTITION_NUM
        aligned_nodes = (len(sorted_node_ids) // SUB_PARTITION_NUM) * SUB_PARTITION_NUM

        for start in range(0, aligned_nodes, SUB_PARTITION_NUM):
            group_sort_indices = np.argsort(group_sum)
            end = start + SUB_PARTITION_NUM
            nodes_to_assign = combined_list[start:end]
            
            for idx, item in enumerate(nodes_to_assign):
                groups[group_sort_indices[idx]].append(item[0])
                groups_outdegree[group_sort_indices[idx]].append(item[1])
                group_sum[group_sort_indices[idx]] += item[1]

        group_sort_indices = np.argsort(group_sum)
        nodes_to_assign = combined_list[aligned_nodes:len(sorted_node_ids)] ## for the remaining edge list.

        for idx, item in enumerate(nodes_to_assign):
            groups[group_sort_indices[idx]].append(item[0])
            groups_outdegree[group_sort_indices[idx]].append(item[1])
            group_sum[group_sort_indices[idx]] += item[1]

        for i in range(SUB_PARTITION_NUM):
            groups_outdegree[i] = np.array(groups_outdegree[i], dtype= np.int32)
            print ("sp = ", i, " outdegree num = ", group_sum[i], " vertex group num = ", len(groups[i]))
            group_sum[i] = (group_sum[i] + 15) // 16 * 16 + 16   ## for 16 alignment
            edge_ptt = np.empty((0,2), dtype=np.int32)
            for group_id in groups[i]:
                lower_bound = group_index[group_id]
                upper_bound = group_index[group_id+1]
                temp_array = edge_array[lower_bound:upper_bound]
                if (len(temp_array) > 0):
                    edge_ptt = np.vstack((edge_ptt, temp_array))

            sorted_idx = np.argsort(edge_ptt[:, 0]) ## sort the edgelist by source vertex id
            edge_ptt = edge_ptt[sorted_idx]

            num_dummy_edges = (16 - len(edge_ptt) % 16) % 16 + 16
            last_source_vertex = edge_ptt[-1, 0]
            dummy_edges = np.array([[last_source_vertex, -2]] * num_dummy_edges, dtype=np.int32)
            edge_ptt = np.vstack((edge_ptt, dummy_edges))

            edge_ptt = np.insert(edge_ptt, 0, np.array([group_sum[i], group_sum[i]], dtype=np.int32), axis=0)
            
            edge_ptt.tofile(s_path + "/p_" + str(partition) + "_sp_" + str(i) + ".bin")
            np.savetxt(s_path + "/p_" + str(partition) + "_sp_" + str(i) + ".txt", edge_ptt, fmt='%d', delimiter=' ')

