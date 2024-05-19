TARGET = hw
DEVICE = xilinx_u250_gen3x16_xdma_3_1_202020_1
FREQ = 250
BUILD_DIR := ./build_dir_$(TARGET)_$(APP)
## need mpicxx to compile host code, if not use mpicxx, pls REMOVE the CXX_MPI def !!
CXX_MPI = true
CXXFLAGS += -DCXX_MPI=$(CXX_MPI)

include host/pcg/Makefile
include host/xcl2/Makefile
include host/unit_test_multi_node_gp/Makefile
include host/log/Makefile
include host/cmdparser/Makefile

include src/coalesce/Makefile
include src/src_cache/Makefile
include test/test_duplicate_512/Makefile
include test/test_common/Makefile

include src/gather_scatter/Makefile
## use pagerank application
include src/pr/Makefile


LDFLAGS += -lxrt_coreutil -luuid
VPP_FLAGS += -DLOG_CACHEUPDATEBURST=5
CXXFLAGS += -DTEST_GP=1

PROCESSOR_NUM=4
SUB_PARTITION_NUM=PROCESSOR_NUM
PARTITION_SIZE=1048576

CXXFLAGS += -DSUB_PARTITION_NUM=$(SUB_PARTITION_NUM)
CXXFLAGS += -DPARTITION_SIZE=$(PARTITION_SIZE)
CXXFLAGS += -DPROCESSOR_NUM=$(PROCESSOR_NUM)

VPP_FLAGS += -DPARTITION_SIZE=$(PARTITION_SIZE)