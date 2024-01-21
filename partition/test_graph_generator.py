import numpy as np

v_burst_len = 32 ## means a burst read can fetch 32 * 512 bit data. = 32*16 = 512 vertics.
E_NUM = 512*1024
test_point_num = 100 ## we test 100 point.
V_E_RATIO = [x * 0.025 for x in range(1, (test_point_num + 1))] ## vertex mem opeartion / edge mem opeartion

s = 0
for v_e in V_E_RATIO:
    print ("v_e_ratio = ", v_e)
    edge_list = np.zeros((E_NUM + 1, 2), dtype=np.int32)
    edge_list[0][0] = E_NUM
    edge_list[0][1] = E_NUM
    
    v_num = E_NUM * 2 * v_e ## each edge has two vertics.
    v_step = v_num / E_NUM

    src_array = np.arange(0, v_num, v_step)
    src_array = np.array(src_array, dtype = np.int32) ## source vertex array 
    
    cyclic_pattern = np.arange(8192) # Create a cyclic pattern
    dest_array = cyclic_pattern[np.arange(E_NUM) % 8192] # Generate the cyclic numpy array
    dest_array = np.array(dest_array, dtype = np.int32) # dest array
    
    edge_list[1:] = np.vstack((src_array, dest_array)).T
    print ("edge file generate done")
    edge_list.tofile("./test_graph/test_vertex_" + str(s) + ".bin")
    np.savetxt("./test_graph/test_vertex_" + str(s) + ".txt", edge_list, fmt='%d', delimiter=' ')
    
    s = s + 1
            
