TARGET = hw
DEVICE = xilinx_u250_gen3x16_xdma_3_1_202020_1
FREQ = 255
## two types: gas and gs.
TYPE ?= gas
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

include src/coalesce/Makefile
include src/src_cache/Makefile
include src/gp/Makefile
include test/test_duplicate_512/Makefile
include test/test_common/Makefile
include src/netgp_common/Makefile
include src/pr/Makefile

## only GAS node need sync and apply kernel.
ifeq ($(TYPE), gas)
	include src/apply/Makefile
	CFG_FILE = ./app/netgp/kernel_gas.cfg
	DEFAULT_CFG = ./app/netgp/kernel_gas.cfg
else
	CFG_FILE = ./app/netgp/kernel_gs.cfg
	DEFAULT_CFG = ./app/netgp/kernel_gs.cfg
endif

## for network stack makefile

INTERFACE := 3 ## using interface 0 and 1
NETLAYERDIR = src/NetLayers/
CMACDIR     = src/Ethernet/
NETLAYERHLS = 100G-fpga-network-stack-core
TEMP_NET_DIR := _x
BINARY_CONTAINER_OBJS += $(NETLAYERDIR)$(TEMP_NET_DIR)/networklayer.xo
VPP_FLAGS += --advanced.param compiler.userPostSysLinkOverlayTcl=$(CMACDIR)post_sys_link.tcl

# enable two interface 0 and 1
BINARY_CONTAINER_OBJS += $(CMACDIR)$(TEMP_NET_DIR)/cmac_1.xo
BINARY_CONTAINER_OBJS += $(CMACDIR)$(TEMP_NET_DIR)/cmac_0.xo

ifeq (u5,$(findstring u5, $(DEVICE)))
	HLS_IP_FOLDER  = $(shell readlink -f ./$(NETLAYERDIR)$(NETLAYERHLS)/synthesis_results_HBM)
else ifeq (u280,$(findstring u280, $(DEVICE)))
	HLS_IP_FOLDER  = $(shell readlink -f ./$(NETLAYERDIR)$(NETLAYERHLS)/synthesis_results_HBM)
else ifeq (u2,$(findstring u2, $(DEVICE)))
	HLS_IP_FOLDER  = $(shell readlink -f ./$(NETLAYERDIR)$(NETLAYERHLS)/synthesis_results_noHBM)
endif

VPP_LDFLAGS = --user_ip_repo_paths $(HLS_IP_FOLDER)

$(CMACDIR)$(TEMP_NET_DIR)/cmac_0.xo:
$(CMACDIR)$(TEMP_NET_DIR)/cmac_1.xo:
	make -C $(CMACDIR) all DEVICE=$(DEVICE) INTERFACE=$(INTERFACE)

$(NETLAYERDIR)$(TEMP_NET_DIR)/networklayer.xo:
	make -C $(NETLAYERDIR) all DEVICE=$(DEVICE)

## for XRT compile
LDFLAGS += -lxrt_coreutil -luuid
VPP_FLAGS += -DLOG_CACHEUPDATEBURST=5
CXXFLAGS += -DTEST_GP=1
CXXFLAGS += -fopenmp

## config.mk for pagerank application
## parameter configuration

## for wcc, HAVE_APPLY_OUTDEG=false, while pr = true
HAVE_APPLY_OUTDEG=true

SUB_PARTITION_NUM=16
PROCESSOR_NUM=4
KERNEL_NUM=16
PARTITION_SIZE=1048576
APPLY_REF_ARRAY_SIZE=1
USE_SCHEDULER=false
USE_APPLY=true
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
