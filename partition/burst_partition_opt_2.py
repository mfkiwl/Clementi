## need to add remap to balance edge number in different partition, and then balance the edge and vertex number in each subpartition.
import numpy as np
import sys
import os

SUB_PARTITION_NUM = 16
burst_len = 32
burst_vertex_num = burst_len * 16  ## 16 = 512 bit / 32 bit

base_path = "/data/yufeng/4node_4SLR_graph_dataset_bp_remap/"  # Replace with the actual file path
dataset_name = ["G25"] ## for large real graph processing

storage_path = "/data/yufeng/4node_4SLR_graph_dataset_bp_remap/"

for dataset in dataset_name:

    file_path = base_path + dataset
    partition_num = 0
    for p in range(100):
        ck_file_name = file_path + "/remap_edge_" + str(p) + ".txt"
        if os.path.exists(ck_file_name):
            partition_num = p + 1
    print ("dataset = ", dataset, " partition_num = ", partition_num)
    
    s_path = storage_path + dataset
    if (os.path.exists(s_path) == True):
        print("Already exists ", s_path)
    else :
        os.mkdir(s_path)
        print("Create directory ", s_path)

    for partition in range(partition_num):
        print ("processing partition ", partition)
        file_name = base_path + dataset + "/remap_edge_" + str(partition) + ".txt"
        edge_array = np.loadtxt(file_name, dtype=np.int32)
        
        ## already finish sort: ascending order. ## important
        vertex_num = edge_array.max() + 1
        print (vertex_num)

        source_nodes = edge_array[:, 0].copy()
        source_nodes //= burst_vertex_num
        source_nodes = np.array(source_nodes, dtype = np.int32)

        # print (source_nodes)

        max_group_id = np.max(source_nodes)
        group_edge_num = np.bincount(source_nodes, minlength=max_group_id+1)
        accumulated_group = np.cumsum(group_edge_num)
        group_index = np.insert(accumulated_group, 0, 0)
        # print (group_index)

        unique_elements, outdegree = np.unique(source_nodes, return_counts=True)

        ## sort the source vertex of subgraph by indegree in a decending order
        sorted_indices = np.argsort(outdegree)[::-1]
        sorted_out_degree_values = outdegree[sorted_indices]
        sorted_node_ids = unique_elements[sorted_indices]

        combined_list = list(zip(sorted_node_ids, sorted_out_degree_values))
        groups = [[] for _ in range(SUB_PARTITION_NUM)]
        group_sum = [0] * SUB_PARTITION_NUM

        ## divide the group by SUB_PARTITION_NUM, partition method => make the vertex number in each group balanced.
        aligned_nodes = (len(sorted_node_ids) // SUB_PARTITION_NUM) * SUB_PARTITION_NUM

        for start in range(0, aligned_nodes, SUB_PARTITION_NUM):
            group_sort_indices = np.argsort(group_sum)
            end = start + SUB_PARTITION_NUM
            nodes_to_assign = combined_list[start:end]
            
            for idx, item in enumerate(nodes_to_assign):
                groups[group_sort_indices[idx]].append(item[0])
                group_sum[group_sort_indices[idx]] += item[1]

        group_sort_indices = np.argsort(group_sum)
        nodes_to_assign = combined_list[aligned_nodes:len(sorted_node_ids)] ## for the remaining edge list.

        for idx, item in enumerate(nodes_to_assign):
            groups[group_sort_indices[idx]].append(item[0])
            group_sum[group_sort_indices[idx]] += item[1]
        
        ## further optimization => adjust edge number to make the execution time in each group balanced. 
        # set iteration number = 100000, up_bound = 1.5 which means the max edge number not exceed (bound*avg_edge)
        iteration = 100000
        up_bound = 1.5
        avg_edge_num = sum(group_sum) // 16
        for iter_num in range(iteration):
            max_edge_num = max(group_sum)
            min_edge_num = min(group_sum)
            if (max_edge_num <= (up_bound * avg_edge_num)):
                break
            else:
                max_group_id = group_sum.index(max_edge_num)
                min_group_id = group_sum.index(min_edge_num)
                last_item = groups[max_group_id].pop()
                last_item_id = np.where(sorted_node_ids == last_item)[0]
                outdeg_value = sorted_out_degree_values[last_item_id]

                former_distance = group_sum[max_group_id] - group_sum[min_group_id]
                group_sum[min_group_id] = group_sum[min_group_id] + outdeg_value
                group_sum[max_group_id] = group_sum[max_group_id] - outdeg_value
                sum_max = max(group_sum)
                sum_min = min(group_sum)

                if ((sum_max - sum_min) < (former_distance)):
                    groups[min_group_id].append(last_item)
                    # print ("move ", last_item, " from ", max_group_id, " to", min_group_id)
                else:
                    groups[max_group_id].append(last_item)
                    group_sum[min_group_id] = group_sum[min_group_id] - outdeg_value
                    group_sum[max_group_id] = group_sum[max_group_id] + outdeg_value
                    print ("iteration ", iter_num, " : finish optimization")
                    break
        
        converted_list = [item.tolist() if isinstance(item, np.ndarray) else item for item in group_sum]
        flattened_list = []
        for item in converted_list:
            if isinstance(item, list):
                flattened_list.extend(item)
            else:
                flattened_list.append(item)
        group_sum = flattened_list
        print ("After optimization, edge number in each group", group_sum)

        ## need to consider duplicated src vertex.
        for i in range(SUB_PARTITION_NUM):
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

