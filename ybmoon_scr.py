#!/usr/bin/env python

import math
import sys
import subprocess
import os
import getopt

init="/scale/cal/home/ybmoon/ybmoon_spec/init"

#profile_uarch="amplxe-cl -collect uarch-exploration -knob dram-bandwidth-limits=true -data-limit=0 -call-stack-mode=user-only -mrte-mode=auto"
profile_uarch="amplxe-cl -collect general-exploration -knob collect-memory-bandwidth=true -knob dram-bandwidth-limits=true -data-limit=0 -call-stack-mode=user-only -mrte-mode=auto"
profile_hotspot='amplxe-cl -collect advanced-hotspots -knob collection-detail=stack-and-callcount -data-limit=0 -target-process=memcached -duration=180 -r'
#profile="amplxe-cl -collect-with runsa -knob event-config=CYCLE_ACTIVITY.CYCLES_L1D_PENDING,CYCLE_ACTIVITY.CYCLES_L2_PENDING,CYCLE_ACTIVITY.STALLS_L1D_PENDING,CYCLE_ACTIVITY.STALLS_L2_PENDING,CPU_CLK_UNHALTED.REF_TSC,CPU_CLK_UNHALTED.THREAD,INST_RETIRED.ANY,L2_DEMAND_RQSTS.WB_HIT,L2_LINES_IN.ALL,L2_LINES_OUT.DEMAND_CLEAN,L2_RQSTS.ALL_CODE_RD,L2_RQSTS.ALL_DEMAND_DATA_RD,L2_TRANS.ALL_PF,L2_TRANS.ALL_REQUESTS,L2_TRANS.L2_FILL,L2_TRANS.L2_WB,L2_TRANS.RFO,MEM_LOAD_UOPS_RETIRED.L2_HIT,MEM_LOAD_UOPS_RETIRED.L2_HIT_PS,L2_BLOCKS.NO_SR,L2_RQSTS.REFERENCE,L2_RQSTS.MISS,L2_RQSTS.CORE_RD_HIT,L2_RQSTS.CORE_RD_MISS"
#profile_unc="amplxe-cl -collect-with runsa -knob event-config=CPU_CLK_UNHALTED.REF_TSC,CPU_CLK_UNHALTED.THREAD,INST_RETIRED.ANY,UNC_M_CAS_COUNT.RD,UNC_M_CAS_COUNT.WR"
#profile_dramcache_miss="amplxe-cl -collect-with runsa -knob event-config=CPU_CLK_UNHALTED.REF_TSC,CPU_CLK_UNHALTED.THREAD,INST_RETIRED.ANY,UNC_M_CAS_COUNT.RD,UNC_M_CAS_COUNT.WR,UNC_M_PMM_RPQ_INSERTS,UNC_M_PMM_WPQ_INSERTS,UNC_M2M_TAG_HIT.NM_RD_HIT_CLEAN,UNC_M2M_TAG_HIT.NM_RD_HIT_DIRTY -data-limit=0 -call-stack-mode=user-only -mrte-mode=auto"
#profile_latency="amplxe-cl -collect-with runsa -knob=analyze-mem-objects=true -knob event-config=MEM_INST_RETIRED.ALL_LOADS_PS,MEM_LOAD_RETIRED.L3_MISS_PS,Total_Latency_MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4,Total_Latency_MEM_TRANS_RETIRED.LOAD_LATENCY_GT_16,MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4,MEM_TRANS_RETIRED.LOAD_LATENCY_GT_16 -data-limit=0 -call-stack-mode=user-only -mrte-mode=auto"

#profile_genex="amplxe-cl -collect general-exploration -knob collect-memory-bandwidth=true -knob dram-bandwidth-limits=false -data-limit=0 -call-stack-mode=user-only -mrte-mode=auto" # for bandwidth measurement
profile="amplxe-cl -collect memory-access -knob sampling-interval=1 -knob analyze-mem-objects=true -knob mem-object-size-min-thres=1 -knob dram-bandwidth-limits=false -call-stack-mode=user-only -data-limit=0"
#vt_object_profile="amplxe-cl -collect hotspots-0 -data-limit=0 -app-working-dir /home/ybmoon/vt_project_test"

profile_root_obj="/home/ybmoon/gapbs_profile/"

memkind_preload="LD_PRELOAD=\"/usr/local/lib/libautohbw.so:/usr/local/lib/libmemkind.so\""

gapbs_apps={"bc": "bc", "cc": "cc", "pr": "pr", "bfs": "bfs", "sssp": "sssp", "bfs": "bfs", "sssp": "sssp", "tc": "tc"}
gapbs_args={"bc": "-i4 -n16", "cc": "-n16", "pr": "-i1000 -t1e-4 -n16", "bfs": "-n64", "sssp": "-d2", "tc": "-n3"}

apppath="/scale/cal/home/ybmoon/numa_autofdo/gapbs/"
rate="4"
# Memory Allocation Node: Local DRAM[0], Remote DRAM[1]
memory_node = "3"

#edit these params
iteration = 1
#appIndex = ["bc", "cc", "pr"]
appIndex = ["cc"]
#appIndex = ["bfs", "sssp", "tc"]
#inputIndex = ["twitter"]
inputIndex = ["kron-27"]

def main(argv):
  for j in appIndex:
    for k in inputIndex:
      exe = '' 
      exedir = apppath#+spec2017_apps[j]+"/run/run_base_refspeed_"+config_n+"-m64.0000"
      exepath = exedir+gapbs_apps[j]
      gaparg = gapbs_args[j]
      if j == "sssp":
        inputarg = "/scale/cal/home/ybmoon/numa_autofdo/gapbs/benchmark/graphs/"+k+".wsg"
      elif j == "tc":
        inputarg = "/scale/cal/home/ybmoon/numa_autofdo/gapbs/benchmark/graphs/"+k+"U.sg"
      else:
        inputarg = "/scale/cal/home/ybmoon/numa_autofdo/gapbs/benchmark/graphs/"+k+".sg"
      outputarg = "/home/ybmoon/gapbs/benchmark/out/"+j+"-"+k+".out"
      #exe ="/scale/cal/home/ybmoon/numa_autofdo/gapbs/wrapper_node1"+" "+memory_node+" "+rate+" "+exedir+" "+exepath+" -f "+inputarg+" "+gaparg
      exe ="/scale/cal/home/ybmoon/numa_autofdo/gapbs/scripts/wrapper/spec2017_wrapper_node1"+" "+memory_node+" "+rate+" "+exedir+" "+exepath+" -f "+inputarg+" "+gaparg
      full1 = exe
      #full1 = profile_uarch+" -r "+profile_path1+" -- "+exe
      print("Full Command: ",full1)
      subprocess.call(init)
      full1=full1.split()
      subprocess.call(full1) # run converting


if __name__ == "__main__":
    main(sys.argv[1:])
