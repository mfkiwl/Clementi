TARGET = hw
DEVICE = xilinx_u250_gen3x16_xdma_3_1_202020_1
FREQ = 250
BUILD_DIR := ./build_dir_$(TARGET)_$(APP)_$(TYPE)

include host/pcg/Makefile
include host/xcl2/Makefile
include host/unit_test_gp/Makefile
include host/log/Makefile
include host/cmdparser/Makefile

include src/coalesce/Makefile
include src/src_cache/Makefile
include test/test_duplicate_512/Makefile
include test/test_common/Makefile

include src/gp/Makefile
include src/pr/Makefile


LDFLAGS += -lxrt_coreutil -luuid
VPP_FLAGS += -DLOG_CACHEUPDATEBURST=5
CXXFLAGS += -DTEST_GP=1

HAVE_APPLY_OUTDEG=true

SUB_PARTITION_NUM=4
PROCESSOR_NUM=1
KERNEL_NUM=1
PARTITION_SIZE=1048576
APPLY_REF_ARRAY_SIZE=1
USE_SCHEDULER=false
CXXFLAGS += -DHAVE_APPLY_OUTDEG=$(HAVE_APPLY_OUTDEG)
CXXFLAGS += -DSUB_PARTITION_NUM=$(SUB_PARTITION_NUM)
CXXFLAGS += -DPARTITION_SIZE=$(PARTITION_SIZE)
CXXFLAGS += -DAPPLY_REF_ARRAY_SIZE=$(APPLY_REF_ARRAY_SIZE)
CXXFLAGS += -DPROCESSOR_NUM=$(PROCESSOR_NUM)
CXXFLAGS += -DUSE_SCHEDULER=$(USE_SCHEDULER)
CXXFLAGS += -DKERNEL_NUM=$(KERNEL_NUM)

VPP_FLAGS += -DHAVE_APPLY_OUTDEG=$(HAVE_APPLY_OUTDEG)
VPP_FLAGS += -DPARTITION_SIZE=$(PARTITION_SIZE)