TARGET = hw
DEVICE = xilinx_u250_gen3x16_xdma_3_1_202020_1
FREQ = 250
## need mpicxx to compile host code, if not use mpicxx, pls REMOVE the CXX_MPI def !!
CXX_MPI = true
CXXFLAGS += -DCXX_MPI=$(CXX_MPI)
BUILD_DIR := ./build_dir_$(TARGET)_$(APP)_$(TYPE)

include host/pcg/Makefile
include host/xcl2/Makefile
include host/network/Makefile
include host/netgp/Makefile
include host/log/Makefile
include host/cmdparser/Makefile

include src/netgp_common/Makefile
include test/test_network/Makefile
include src/pr/Makefile
include src/apply/Makefile

## for XRT compile
LDFLAGS += -lxrt_coreutil -luuid
VPP_FLAGS += -DLOG_CACHEUPDATEBURST=5
CXXFLAGS += -DTEST_GP=1
CXXFLAGS += -fopenmp

HAVE_APPLY_OUTDEG=true

SUB_PARTITION_NUM=4
PROCESSOR_NUM=1
KERNEL_NUM=4
PARTITION_SIZE=1048576
APPLY_REF_ARRAY_SIZE=1
USE_SCHEDULER=false
USE_APPLY=true
NOT_USE_GS=true
CXXFLAGS += -DNOT_USE_GS=$(NOT_USE_GS)
CXXFLAGS += -DUSE_APPLY=$(USE_APPLY)
CXXFLAGS += -DHAVE_APPLY_OUTDEG=$(HAVE_APPLY_OUTDEG)
CXXFLAGS += -DSUB_PARTITION_NUM=$(SUB_PARTITION_NUM)
CXXFLAGS += -DPARTITION_SIZE=$(PARTITION_SIZE)
CXXFLAGS += -DAPPLY_REF_ARRAY_SIZE=$(APPLY_REF_ARRAY_SIZE)
CXXFLAGS += -DPROCESSOR_NUM=$(PROCESSOR_NUM)
CXXFLAGS += -DUSE_SCHEDULER=$(USE_SCHEDULER)
CXXFLAGS += -DKERNEL_NUM=$(KERNEL_NUM)

VPP_FLAGS += -DHAVE_APPLY_OUTDEG=$(HAVE_APPLY_OUTDEG)
VPP_FLAGS += -DPARTITION_SIZE=$(PARTITION_SIZE)
