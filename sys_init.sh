#!/bin/bash

SYSTEM_INIT(){
  sudo sh -c "echo 0 > /proc/sys/kernel/yama/ptrace_scope"
  sudo sh -c "echo 1 > /proc/sys/vm/drop_caches"
  sudo sh -c "echo 0 > /proc/sys/kernel/kptr_restrict"
  sudo sh -c "echo -1 > /proc/sys/kernel/perf_event_paranoid"
  sudo sh -c "echo 0 > /proc/sys/kernel/nmi_watchdog"
  numactl -H
}

AMBARI_STOP(){
  sudo sh -c "ambari-server stop"
  sudo sh -c "/etc/init.d/postgresql stop"
  sudo sh -c "/etc/init.d/mysql stop"
  sudo sh -c "service apache2 stop"
}

VTUNE_DRIVER(){
  sudo sh -c "cd /usr/src/intel/vtune_amplifier_2018.4.0.573462/sepdk/src/;./build-driver -ni;./insmod-sep -r -g scale-members"
}


## Main
SYSTEM_INIT
#AMBARI_STOP
#VTUNE_DRIVER
