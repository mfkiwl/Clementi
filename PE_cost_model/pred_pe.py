import numpy as np
import matplotlib.pyplot as plt
import random
import os
import argparse

parser = argparse.ArgumentParser(description="node number")
parser.add_argument("dataset", type=str, help="dataset name")
args = parser.parse_args()

DATASET_NAME = args.dataset
PATH = "./m_access/"
np.set_printoptions(precision=2)

def getPartitionNum (dataset):
    ref_path = "/data/yufeng/single_4SLR_graph_dataset_bp2/" + dataset
    for p_idx in range(100):
        file_name = ref_path + "/p_" + str(p_idx) + "_sp_0.txt"
        if (os.path.exists(file_name) == False):
            return p_idx


## load dataset hyper-parameter v/e + e + v
## Note that edge_op: edge access memory operation number
## Note that vertex_op: vertex access memory operation number
## Note that v_e_ratio: operation ratio

v_e_ratio = np.loadtxt(PATH + DATASET_NAME + "_v_e_ratio.txt").reshape((-1,))
edge_op = np.loadtxt(PATH + DATASET_NAME + "_e_op.txt").reshape((-1,))
vertex_op = np.loadtxt(PATH + DATASET_NAME + "_v_op.txt").reshape((-1,))

## estimate execution time for each partition
# V <= 0.192*E + 130686; MTEPS -> E
# V > 0.192*E + 130686; MTEPS -> E & V/E
original_tasks = []
partitionNum = getPartitionNum(DATASET_NAME)

print ("run ", DATASET_NAME)
for p_idx in range(partitionNum):
    if (vertex_op[p_idx] <= (0.192 * edge_op[p_idx] + 130686)):
        MTEPS = 1300 / ((4*1024*1024*0.0895 / edge_op[p_idx]) + 0.924)
    else:
        MTEPS = 1200 / (2.375 * v_e_ratio[p_idx] + (4*1024*1024*0.0155 / edge_op[p_idx]) + 0.468)
    exe_time = np.int32(edge_op[p_idx] * 8 / MTEPS)  ## each edge mem operation has 8 edges, ms
    print("[" + str(p_idx) + "]  device  time = ", exe_time)
    # print ("partition = ", p_idx, " MTEPS = ", MTEPS, " exe_time = ", exe_time)

