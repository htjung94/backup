#!/bin/bash

SYSTEM_INIT(){
  sudo sh -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"
  sudo sh -c "echo 1 > /proc/sys/vm/drop_caches"
  sudo sh -c "echo 0 > /proc/sys/kernel/kptr_restrict"
  sudo sh -c "echo -1 > /proc/sys/kernel/perf_event_paranoid"
  sudo sh -c "echo 0 > /proc/sys/kernel/nmi_watchdog"
  sudo sh -c "echo 0 > /proc/sys/kernel/randomize_va_space"
  sudo sh -c "echo 5000000 > /proc/sys/kernel/perf_event_max_sample_rate"

  ulimit -s unlimited
  numactl -H
  sleep 3
}


## Main
SYSTEM_INIT
