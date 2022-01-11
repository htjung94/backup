#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>
#include <sys/types.h>
#include <time.h>
#include <sys/time.h>
#include <inttypes.h>
#include <unistd.h>
#include <sched.h>
#include <numa.h>
#include <numaif.h>
#include <fcntl.h>

typedef struct thread_args {
  int core_id;
  int mem_node;
  struct bitmask *mem_bmp;
  char *path;
  char *exe_path;
  char **option;   
  char *input;
} thread_t;

uint64_t get_elapsed (struct timespec *start, struct timespec *end) {
  uint64_t duration;
  if (start->tv_nsec > end->tv_nsec)
    duration = (uint64_t)(end->tv_sec - 1 - start->tv_sec) * 1000000000 +
      (1000000000 + end->tv_nsec - start->tv_nsec);
  else
    duration = (uint64_t)(end->tv_sec - start->tv_sec) * 1000000000 +
      (end->tv_nsec - start->tv_nsec);
  return duration;
}

void *process_gen (void *args) {
  printf("Process Start\n");
  thread_t *th_arg = (thread_t *)args;
  char *exe_path = th_arg->exe_path;
  char *path = th_arg->path;
  char* argv = th_arg->option;
  int mem_node = th_arg->mem_node;
  struct bitmask *mem_bmp = th_arg->mem_bmp;
  struct timespec start, end;
  uint64_t elapse_time;
  int node;
  int core;
  int stat;
  int frd;
  char buff[1024];

  cpu_set_t cpu_mask;
  CPU_ZERO(&cpu_mask);
  CPU_SET(4*th_arg->core_id, &cpu_mask);
  CPU_SET(4*th_arg->core_id+2, &cpu_mask);

  sched_setaffinity(0, sizeof(cpu_set_t), &cpu_mask);

  if (set_mempolicy(MPOL_PREFERRED, mem_bmp->maskp, mem_bmp->size + 1) < 0)
//if (set_mempolicy(MPOL_BIND, mem_bmp->maskp, mem_bmp->size + 1) < 0)
   numa_error("set_mempolicy");

  clock_gettime(CLOCK_REALTIME, &start);
  pid_t pid = fork();
  //printf("PID:%d\n",pid);
  core = sched_getcpu();
  node = numa_node_of_cpu(core);
  printf("node[%d].core[%2d]\n", node, core);

  if(pid < 0) {
    perror("Fork error\n");
    exit(1);
  } else if(pid==0) {
    //printf("exe: CHILD My pid is:%d  my parent pid:%d\n", getpid(), getppid());
    chdir(path);
    getcwd(buff, 1024);
    //printf("directory:%s\n",buff );
    if(th_arg->input != NULL) {
      //printf("input file:%s\n",th_arg->input);
      int fd = open(th_arg->input, O_RDONLY);
      frd = dup2(fd,STDIN_FILENO);
      close(fd);
    }
    //printf ("exe_path: %s\n", exe_path);
    stat = execvp(exe_path,th_arg->option);
    printf("Execution END: %d\n", stat);
    close(frd);	
  } else {
    int res;
    printf("Wait PID: %d\n", pid);
    waitpid(pid, &res, 0);
  }

  clock_gettime(CLOCK_REALTIME, &end);
  elapse_time = get_elapsed(&start, &end);
  printf("Execution Time (%d) => %.2lf ns\n", core, (double)elapse_time);
}

int main(int argc, char *argv[]) {
  int i, j, k, temp;
  char *options[argc-2];
  char nul;
  char path[48][1024],buf[2];
  char *input=(char*)0;
  int mem_mode = 0;   // Default: Local Allocation

  if (argc < 5) {
    printf("<mem mode> <#copy> <file path> <file name> <options>\n");
    exit(1);
  }

  int core = sched_getcpu();
  int node = numa_node_of_cpu(core);
  //printf("node[%d].core[%2d]\n", node, core);
  //printf("argc:%d\n",argc);
  char* file = argv[4];
  //printf("Original Execution File:   %s\n", file);

  // Number of program
  int program_num = atoi(argv[2]); 
  for(i = 0; i < 48; i++){
    strcpy(path[i], argv[3]);
  }
  printf("Num of Programs:  %d\n", program_num);
  options[0] = file;
  //printf("Program Path:     %s\n", path[0]);
  //printf("Progarm Options:  %s\n", options[0]);

  int cmp;
  for(i=1; i<argc-4; i++) {
    printf("i:%d, argv[%d]:%s\n",i, i+4,argv[i+4]);
    cmp = strcmp(argv[i+4],"$"); //input file stream
    if(cmp==0){
      printf("argv:%s\n",argv[i+4]);
      input = argv[i+5];
      printf("input:%s\n",input);
      break;		
    } 
    options[i] = argv[i+4];
  }

  thread_t th_args[program_num];
  pthread_t threads[program_num];
  pid_t cur_pid = getpid(); 

  int tmp_node = atoi(argv[1]);
  printf("tmp_node: %d\n", tmp_node);
  if (tmp_node == 0) {
    mem_mode = 0;     // Local memory Allocation
    printf ("Local DRAM Allocation\n");
  } else if (tmp_node == 1) {
    mem_mode = 1;
    printf ("Remote DRAM Allocation\n");
  } else {
    printf ("Error: Memory Allocation Error\n"); 
  }

  temp = atoi(((char*)path[0] + strlen(path) -2));

  for(i=0; i<program_num; i++) {
    th_args[i].core_id = i;
    th_args[i].mem_node = mem_mode;
    th_args[i].input = input;
    snprintf(buf,4,"%02d",temp);
    strcpy(path[i] + strlen(path) -2, buf);
    th_args[i].path = path[i];
    th_args[i].exe_path = file;
    th_args[i].option = options;
    //printf("Directory [%d]:   %s\n", i, th_args[i].path);
  }

  for (i = 0; i < program_num; i++) {
    if (th_args[i].mem_node == 0) {
      struct bitmask *mem_node0 = numa_parse_nodestring("2");
      th_args[i].mem_bmp = mem_node0;
    } else if (th_args[i].mem_node == 1) {
      struct bitmask *mem_node1 = numa_parse_nodestring("1,3");
      th_args[i].mem_bmp = mem_node1;
    }
  }

  for (i = 0; i < program_num; i++) {
    pthread_create(&(threads[i]), NULL, process_gen, (void *)(&th_args[i]));
  }

  for (i = 0; i < program_num; i++) {
    pthread_join(threads[i], NULL);
  }

  return 0;
}
