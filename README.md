# Clementi
### Clementi: A Scalable Multi-FPGA Graph Processing Framework

## Introduction
Clementi is a scalable, multi-FPGA based graph processing framework designed to achieve near-linear scalability. By overlapping communication with computation, Clementi optimizes end-to-end performance. Additionally, leveraging a custom hardware architecture in FPGA, we propose a performance model and a workload scheduling method to minimize execution time discrepancies among FPGAs. Our experimental results demonstrate that Clementi significantly outperforms existing multi-FPGA frameworks, achieving speedups ranging from 1.86× to 8.75×, and exhibits near-linear scalability as the number of FPGAs increases.

## Prerequisites
Clementi development utilizes the Xilinx Vitis toolset. Key components include:
- **Xilinx XRT** version 2.14.354
- **Vitis v++** at v2021.2 (64-bit)

The framework is executed on the HACC cluster at NUS. For detailed information and access to this cluster, please refer to the [HACC_NUS website](https://xacchead.d2.comp.nus.edu.sg/). Each FPGA on this cluster is paired with a virtual CPU node, utilizing OpenMPI for distributed execution. The specific version used is Open MPI 4.1.4, and the system incorporates four [Xilinx U250 FPGAs](https://docs.amd.com/r/en-US/ug1120-alveo-platforms/U200-Gen3x16-XDMA-base_2-Platform).

## System Overview
![Clementi Overview](images/Clementi_overview.png)
Clementi utilizes a three-phase approach to process large graphs on multi-FPGA platforms with a ring topology:
1. **Graph Partitioning:** The input edge list is initially partitioned into subgraphs using a 2D partitioning method that integrates interval-shard and input-aware partition.
2. **Subgraph Assignment:** A performance model predicts execution times for each subgraph, which informs a greedy-based scheduling algorithm to ensure balanced workloads across the FPGAs.
3. **Concurrent Processing:** Each FPGA concurrently processes its assigned subgraphs, overlapping gather-scatter and global apply stages to optimize performance.

## Initialization
To begin working with Clementi, clone the repository using the following command:
```bash
git clone --recursive https://github.com/Xtra-Computing/Clementi.git
```
## Build Hardware
```bash
# Load the Xilinx Vitis and XRT settings
source /opt/Xilinx/Vitis/2021.2/settings64.sh
source /opt/xilinx/xrt/setup.sh

# Build all components for the netgp_parallel application
make all app=netgp_parallel
```

## Build Software
```bash
#If you only need to build software code, use the following command:
make host app=netgp_parallel
```

## Test
Run the hardware single graph processor script to test the system. Ensure that you have the correct OpenMPI settings configured before running the multiple FPGAs demo:
```bash
./hw_single_gp.sh
```

## Repository Structure

- `app` - Contains applications used within the project.
- `host` - Host files for the XRT driver.
- `images` - Images used in the README documentation.
- `mk` - Directory containing makefiles.
- `partition` - Includes the input-aware partition method and performance model.
- `src` - Hardware files for each block in the Clementi framework.
- `test` - Contains test files and scripts.
- `host_file` - Host files used in MPI code.