import numpy as np
import matplotlib.pyplot as plt
import random
import os
import argparse

parser = argparse.ArgumentParser(description="node number")
parser.add_argument("dataset", type=str, help="dataset name")
parser.add_argument("node_num", type=np.int32, help="node number")
args = parser.parse_args()

NODE_NUM = args.node_num
DATASET_NAME = args.dataset
APPLY_TIME = 2
SLR_PER_NODE = 4
DUMMY_TASK = {'partition_id': 0xffff, 'exe_time': 2} ## set the minimal time interval
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

## estimate execution time for each partition
# V <= 0.192*E + 130686; MTEPS -> E
# V > 0.192*E + 130686; MTEPS -> E & V/E
original_tasks = []
partitionNum = getPartitionNum(DATASET_NAME)

for p_idx in range(partitionNum):
    if (vertex_op[p_idx] <= (0.192 * edge_op[p_idx] + 130686)):
        MTEPS = 1200 / ((4*1024*1024*0.0895 / edge_op[p_idx]) + 0.924)
    else:
        MTEPS = 1200 / (2.375 * v_e_ratio[p_idx] + (4*1024*1024*0.0155 / edge_op[p_idx]) + 0.468)
    exe_time = np.int32(edge_op[p_idx] * 8 / MTEPS / SLR_PER_NODE // 1000)  ## each edge mem operation has 8 edges, ms
    # print ("partition = ", p_idx, " MTEPS = ", MTEPS, " exe_time = ", exe_time)
    original_tasks.append({"partition_id" : p_idx, "exe_time" : exe_time / NODE_NUM})

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

## task scheduler
    
workstations_opt = [[] for _ in range(NODE_NUM)] ## used for store partition id
exe_time_per_worker_opt = np.zeros(NODE_NUM, dtype=np.float64)

tasks = original_tasks.copy()
while tasks:
    current_task = tasks.pop(0)
    for node_idx in range(NODE_NUM):
        workstations_opt[node_idx].append(current_task['partition_id'])
        exe_time_per_worker_opt[node_idx] = exe_time_per_worker_opt[node_idx] + current_task['exe_time'] + APPLY_TIME

print ("Name ", DATASET_NAME, " baseline, Node number = ", NODE_NUM, " max_time = ", exe_time_per_worker_opt[0])
# for n_idx in range(NODE_NUM):
#     print ("Node ", n_idx, " exe_time = ", exe_time_per_worker_opt[n_idx], " task order : ", workstations_opt[n_idx])

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
            if (p_id == 0xffff):
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
                ## GS task
                color = 'grey'
                task_time = [task['exe_time'] for task in original_tasks if task['partition_id'] == p_id][0]
                end_point = timeline + task_time
                ax.plot([timeline, end_point], [machine_index, machine_index], color=color, linewidth=30, solid_capstyle='butt')

                mid_time = timeline + (end_point - timeline) / 2
                text_color = 'black' if color == '#FFFFFF' else 'white'
                ax.text(mid_time, machine_index, str(p_id), color=text_color, verticalalignment='center', horizontalalignment='center')
                
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
    plt.savefig("machine_task_timeline_baseline.png", dpi=300)

