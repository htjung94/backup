#!/usr/bin/env python
import math
import sys
import subprocess
import signal
import os
import getopt

#vprofiler="amplxe-cl -collect hotspots -knob enable-stack-collection=true -knob sampling-mode=sw -knob stack-size=0 -call-stack-mode=user-only -data-limit=0"
#vprofiler="amplxe-cl -collect general-exploration -knob collect-memory-bandwidth=true -knob dram-bandwidth-limits=false -data-limit=0 -call-stack-mode=user-only -mrte-mode=auto -knob sampling-interval=0.1"
#profiler="/scale/cal/home/djoh0967/perf/perf c2c record -F 100000"
#vprofiler="amplxe-cl -collect memory-access -knob analyze-mem-objects=true -knob mem-object-size-min-thres=1 -knob dram-bandwidth-limits=false -data-limit=0 -knob sampling-interval=0.1"

numactl="numactl -C 0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38 -m 0"

## Application Info
apps={"cfrac": "cfrac",
        "espresso": "espresso",
        "barnes": "barnes",
        "alloc-test1": "alloc-test",
        "alloc-testN": "alloc-test",
        "larsonN": "larson",
        "sh6benchN": "sh6bench",
        "sh8benchN": "sh8bench",
        "xmalloc-testN": "xmalloc-test",
        "cache-scratch1": "cache-scratch",
        "cache-scratchN": "cache-scratch",
        "mstressN": "mstress"}


app_args={"cfrac": "17545186520507317056371138836327483792789528",
        "espresso": "../../bench/espresso/largest.espresso",
        "barnes": "",
        "alloc-test1": "1",
        "alloc-testN": "16",
        "larsonN": "5 8 1000 5000 100 4141 24",
        "sh6benchN": "20",
        "sh8benchN": "20",
        "xmalloc-testN": "-w 96 -t 5 -s 64",
        "cache-scratch1": "1 1000 1 2000000 20",
        "cache-scratchN": "20 1000 1 2000000 20",
        "mstressN": "20 100 10"}

malloc_path={"mi" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/mimalloc/out/release/libmimalloc.so",
        "dmi" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/mimalloc/out/debug/libmimalloc-debug.so",
        "smi" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/mimalloc/out/secure/libmimalloc-secure.so",
        "tc" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/gperftools/.libs/libtcmalloc_minimal.so",
        "je" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/jemalloc/lib/libjemalloc.so",
        "tbb" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/tbb/build/linux_intel64_gcc_cc7.5.0_libc2.27_kernel5.3.0_release/libtbbmalloc_proxy.so.2",
        "sn" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/snmalloc/release/libsnmallocshim.so",
        "pre_sn" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/pre_snmalloc/release/libsnmallocshim.so",
        "sn_0.4.1" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/snmalloc_0.4.1/release/libsnmallocshim.so",
        "rp" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/rpmalloc/bin/linux/release/x86-64/librpmallocwrap.so",
        "hd" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/Hoard/src/libhoard.so",
        "mesh" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/mesh/libmesh.so",
        "nomesh" : "/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/extern/nomesh/libmesh.so"}


appIndex = ["cfrac", "espresso", 
        "alloc-test1", "alloc-testN", "larsonN",
        "sh6benchN", "sh8benchN", "xmalloc-testN",
        "cache-scratch1", "cache-scratchN"]

#mallocIndex = ["mi", "smi", "tc", 
#        "je", "tbb", "sn", 
#        "rp", "hd", "mesh", "nomesh"]


#appIndex = ["cache-scratch1", "cache-scratchN"]
#appIndex = ["sh6benchN"]


#mallocIndex = ["mi", "sn"]
mallocIndex = ["pre_sn", "sn", "sn_0.4.1", "mi"]

outputdir="/scale/cal/home/htjung/malloc_profiling/malloc_output/"
apppath="/scale/cal/home/htjung/malloc_profiling/mimalloc-bench/out/bench/"


def main(argv):
  for lm in range(0,6):
    for j in appIndex:
        for k in mallocIndex:

            ## Initial Process
            init    = '/scale/cal/home/htjung/environment/init.sh'
            init    = init.split()
            subprocess.call(init)

            ## Benchmark Setup
            exe     = ''
            exedir  = apppath
            exepath = exedir+apps[j]
            output  = outputdir+j+"_"+k+"[run].out"
            vtune_output = outputdir+j+"_"+k+"_"+str(lm)+"_vtune"
            perf_output = outputdir+j+"_"+k+".data"

            ## Command Setup 
            env     = "env LD_PRELOAD="+malloc_path[k]
            exe     = "/usr/bin/time -a -o "+output+" "+env+" "+numactl+" "+exepath+" "+app_args[j]
            #exe     = env+" "+numactl+" "+exepath+" "+app_args[j]
            #exe     = vprofiler+" -r "+vtune_output+" -- "+exe
            #exe = vprofiler+" -- "+exe
            #exe     = profiler+" -o "+perf_output+" -- "+exe

            print(exe)
            exe     = exe.split()

            ## Run Benchmarks
            #subprocess.call(exe, stdout = open(output,"w"))
            subprocess.call(exe)


if __name__ == "__main__":
    main(sys.argv[1:])
