include mk/phase_init.mk

app ?= gp
APP :=  $(basename $(app:app/%=%))
APP :=  $(basename $(APP:%/=%))

include mk/phase_app.mk
include mk/phase_misc.mk
include mk/phase_sw.mk
include mk/phase_hw.mk