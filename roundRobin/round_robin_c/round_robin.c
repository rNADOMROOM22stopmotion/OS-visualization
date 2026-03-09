#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>



typedef struct {
    int pid;
    int arrival_time;
    int burst_time;
    int remaining_time;
    int completion_time;
    int turn_around_time;
    int waiting_time;
} Process;

typedef struct Node {
    Process* p;
    struct Node* next;
} Node;

Node* front = NULL;
Node* rear = NULL;

void enqueue(Process* p) {
    Node* temp = (Node*)malloc(sizeof(Node));
    temp->p = p;
    temp->next = NULL;
    if (rear == NULL) {
        front = rear = temp;
        return;
    }
    rear->next = temp;
    rear = temp;
}

Process* dequeue() {
    if (front == NULL) return NULL;
    Node* temp = front;
    Process* p = temp->p;
    front = front->next;
    if (front == NULL) rear = NULL;
    free(temp);
    return p;
}

int is_empty() {
    return front == NULL;
}

int processes_generated = 0;
int next_arrival = 0;

void check_arrivals(int sys_time, int mode2, int total_processes, Process* all_processes) {
    while ((!mode2 || processes_generated < total_processes) && sys_time >= next_arrival) {
        Process* p = (Process*)malloc(sizeof(Process));
        p->pid = processes_generated + 1;
        p->arrival_time = sys_time;
        p->burst_time = (rand() % 10) + 3; // 3 to 12
        p->remaining_time = p->burst_time;
        p->completion_time = 0;
        p->turn_around_time = 0;
        p->waiting_time = 0;
        
        if (mode2 && all_processes != NULL) {
            all_processes[processes_generated] = *p;
        }
        
        enqueue(p);
        processes_generated++;
        
        next_arrival = sys_time + (rand() % 3) + 2; // Arrives in 2 to 4 seconds
    }
}

int main(int argc, char* argv[]) {
    int mode2 = 0;
    int total_processes = 0;
    int time_quantum = 3; // Default value
    
    for(int i = 1; i < argc; i++) {
        if(strcmp(argv[i], "--processes") == 0 && i + 1 < argc) {
            mode2 = 1;
            total_processes = atoi(argv[i+1]);
            i++;
        } else if(strcmp(argv[i], "--tq") == 0 && i + 1 < argc) {
            time_quantum = atoi(argv[i+1]);
            if (time_quantum <= 0) time_quantum = 3; // Fallback
            i++;
        }
    }

    srand(time(NULL));
    
    int sys_time = 0;
    int processes_completed = 0;
    int was_idle = 0;
    
    Process* current_process = NULL;
    int time_in_quantum = 0;
    
    Process* all_processes = NULL;
    if (mode2 && total_processes > 0) {
        all_processes = (Process*)malloc(sizeof(Process) * total_processes);
    }
    
    if (mode2) {
        printf("Starting Round Robin (Mode 2) with %d random processes. Target Burst Time: 3-12s, Arrival Interval: 2-4s. Time Quantum = %d\n\n", total_processes, time_quantum);
    } else {
        printf("Starting Round Robin (Mode 1) with infinite random processes. Target Burst Time: 3-12s, Arrival Interval: 2-4s. Time Quantum = %d\n\n", time_quantum);
    }

    char gantt_buf[4096] = ""; // Large buffer for gantt output
    char temp_buf[64];
    
    if (!mode2) {
        printf("--- Gantt Chart ---\n");
        printf("[0] ");
        fflush(stdout);
    } else {
        sprintf(temp_buf, "[0] ");
        strcat(gantt_buf, temp_buf);
    }
    
    // Check arrivals at t=0
    check_arrivals(sys_time, mode2, total_processes, all_processes);
    
    while(1) {
        // Termination condition for Mode 2
        if (mode2 && processes_completed >= total_processes) {
            break;
        }

        // Schedule new process if CPU is free
        if (current_process == NULL && !is_empty()) {
            if (was_idle) {
                if (!mode2) {
                    printf("[%d] ", sys_time); // Close IDLE block
                } else {
                    sprintf(temp_buf, "[%d] ", sys_time);
                    strcat(gantt_buf, temp_buf);
                }
                was_idle = 0;
            }
            
            Process* next_p = front->p; // Peak at the next one
            
            // We only print the start of the block if it's a NEW process
            // Because if it's the SAME process, and we didn't print the end bracket earlier,
            // we should NOT print a new start block.
            // Except for the very first process at t=0
            static int last_pid = -1;
            
            current_process = dequeue();
            
            if (last_pid != current_process->pid) {
                 if (!mode2) {
                     printf("| P%d ", current_process->pid);
                     fflush(stdout);
                 } else {
                     sprintf(temp_buf, "| P%d ", current_process->pid);
                     strcat(gantt_buf, temp_buf);
                 }
            }
            last_pid = current_process->pid;
            
            time_in_quantum = 0;
        }
        
        // Execute CPU cycle
        if (current_process != NULL) {
            current_process->remaining_time--;
            time_in_quantum++;
            sys_time++;
            
            // Immediately check for new arrivals at this exact sys_time 
            // before the current process can be put back in the back of the queue
            check_arrivals(sys_time, mode2, total_processes, all_processes);
            
            // Check process state
            if (current_process->remaining_time == 0) {
                if (!mode2) {
                    printf("[%d] ", sys_time);
                    fflush(stdout);
                } else {
                    sprintf(temp_buf, "[%d] ", sys_time);
                    strcat(gantt_buf, temp_buf);
                }
                
                current_process->completion_time = sys_time;
                current_process->turn_around_time = current_process->completion_time - current_process->arrival_time;
                current_process->waiting_time = current_process->turn_around_time - current_process->burst_time;
                
                // Update the array for final table output
                if (mode2 && all_processes != NULL) {
                    for(int i = 0; i < total_processes; i++) {
                        if (all_processes[i].pid == current_process->pid) {
                            all_processes[i] = *current_process;
                            break;
                        }
                    }
                }
                
                free(current_process);
                current_process = NULL;
                processes_completed++;
                
            } else if (time_in_quantum == time_quantum) {
                // Preempted
                enqueue(current_process);
                current_process = NULL;
                
                // Only print the timestamp if the schedule actually switches to a NEW process
                // Or if it becomes idle
                if ((front != NULL && front->p->pid != rear->p->pid) || is_empty()) {
                     if (!mode2) {
                         printf("[%d] ", sys_time);
                         fflush(stdout);
                     } else {
                         sprintf(temp_buf, "[%d] ", sys_time);
                         strcat(gantt_buf, temp_buf);
                     }
                }
            }
        } else {
            // Idle CPU
            if (!was_idle) {
                if (!mode2) {
                    printf("| IDLE ");
                    fflush(stdout);
                } else {
                    sprintf(temp_buf, "| IDLE ");
                    strcat(gantt_buf, temp_buf);
                }
                was_idle = 1;
            }
            sys_time++;
            check_arrivals(sys_time, mode2, total_processes, all_processes);
        }
        
        // Mode 1 slow simulation animation
        if (!mode2) {
            usleep(200000); // 0.2 seconds per time unit
        }
    }
    
    printf("\n");
    
    // Print summary stats table for Mode 2
    if (mode2) {
        printf("--- Gantt Chart ---\n");
        printf("%s\n\n", gantt_buf);
        
        printf("--- Process Execution Details ---\n");
        printf("PID\tArrival\tBurst\tCompletion\tTAT\tWT\n");
        printf("------------------------------------------------------------\n");
        
        float avg_tat = 0, avg_wt = 0;
        
        for(int i = 0; i < total_processes; i++) {
            printf("P%d\t%d\t%d\t%d\t\t%d\t%d\n", 
                all_processes[i].pid, 
                all_processes[i].arrival_time, 
                all_processes[i].burst_time,
                all_processes[i].completion_time,
                all_processes[i].turn_around_time,
                all_processes[i].waiting_time);
                
            avg_tat += all_processes[i].turn_around_time;
            avg_wt += all_processes[i].waiting_time;
        }
        
        printf("------------------------------------------------------------\n");
        printf("Average TAT: %.2f\n", avg_tat / total_processes);
        printf("Average WT: %.2f\n", avg_wt / total_processes);
        
        free(all_processes);
    }
    
    return 0;
}
