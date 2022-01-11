#!/bin/bash 

TEMP_PATH=/scale/cal/home/ybmoon/tools/ndctl
NDCTL=${TEMP_PATH}/ndctl/ndctl
DAXCTL=${TEMP_PATH}/daxctl/daxctl
#NDCTL=ndctl
#DAXCTL=daxctl

${NDCTL} disable-namespace namespace1.0
${NDCTL} disable-namespace namespace0.0

${NDCTL} destroy-namespace namespace0.0
${NDCTL} destroy-namespace namespace1.0

${NDCTL} disable-region all

${DAXCTL} migrate-device-model

lsmod | grep dax 


modprobe -r dax_pmem_compat

lsmod | grep dax

${NDCTL} enable-region all

ipmctl show -region


${NDCTL} create-namespace --mode devdax --map mem
${NDCTL} create-namespace --mode devdax --map mem

${DAXCTL} reconfigure-device --mode=system-ram --region=0 all
${DAXCTL} reconfigure-device --mode=system-ram --region=1 all


numactl -H
