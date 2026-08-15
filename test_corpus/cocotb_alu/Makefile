# cocotb Makefile for Verilator & SystemVerilog ALU

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/../alu_module/alu.sv

TOPLEVEL = alu
MODULE = test_alu
WAVES = 1
COMPILE_ARGS += --trace
SIM_ARGS += --trace

include /home/virtual/miniconda3/lib/python3.13/site-packages/cocotb_tools/makefiles/Makefile.sim
