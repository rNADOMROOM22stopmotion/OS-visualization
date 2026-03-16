#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX 100

typedef struct {
    int pid;
    double at, bt, pr;
    double ct, wt, tat;
    int completed;
} Process;

int main(int argc, char *argv[]) {

    int n, done = 0;
    Process p[MAX];
    double time_val = 0;
    double total_wt = 0, total_tat = 0;
    
    int is_auto = (argc == 1);

    if (is_auto) {
        n = 5;
        srand(time(NULL));
        for (int i = 0; i < n; i++) {
            p[i].pid = i + 1;
            p[i].completed = 0;
            p[i].at = rand() % 6;       // Arrival time: 0 to 5
            p[i].bt = (rand() % 10) + 1; // Burst time: 1 to 10
            p[i].pr = (rand() % 5) + 1;  // Priority: 1 to 5 (lower is better)
        }
        printf("Operating in Automatic Mode: Generating %d random processes...\n", n);
    } else {
        /* -------- Validate Number of Processes -------- */
        do {
            printf("Enter number of processes: ");
            scanf("%d", &n);

            if(n <= 0)
                printf("Invalid! Number of processes must be greater than 0.\n");

        } while(n <= 0);


        /* -------- Input Section with Validation -------- */
        for(int i = 0; i < n; i++) {

            p[i].pid = i + 1;
            p[i].completed = 0;

            printf("\nProcess P%d\n", i + 1);

            /* Arrival Time Validation */
            do {
                printf("Arrival Time: ");
                scanf("%lf", &p[i].at);

                if(p[i].at < 0)
                    printf("Invalid! Arrival Time cannot be negative.\n");

            } while(p[i].at < 0);

            /* Burst Time Validation */
            do {
                printf("Burst Time: ");
                scanf("%lf", &p[i].bt);

                if(p[i].bt <= 0)
                    printf("Invalid! Burst Time must be greater than 0.\n");

            } while(p[i].bt <= 0);

            /* Priority Validation */
            do {
                printf("Priority (lower number = higher priority): ");
                scanf("%lf", &p[i].pr);

                if(p[i].pr < 0)
                    printf("Invalid! Priority cannot be negative.\n");

            } while(p[i].pr < 0);
        }
    }

    printf("\n====== Priority Scheduling (Non-Preemptive) ======\n");
    printf("\nGantt Chart:\n|");

    /* -------- Priority Scheduling Logic -------- */
    while(done < n) {

        int idx = -1;
        double highest = 1e9;

        for(int i = 0; i < n; i++) {
            if(!p[i].completed && p[i].at <= time_val) {
                if(p[i].pr < highest) {
                    highest = p[i].pr;
                    idx = i;
                }
            }
        }

        if(idx == -1) {
            time_val++;  // CPU Idle
        }
        else {
            printf("  P%d  |", p[idx].pid);

            p[idx].ct = time_val + p[idx].bt;
            p[idx].tat = p[idx].ct - p[idx].at;
            p[idx].wt = p[idx].tat - p[idx].bt;

            total_wt += p[idx].wt;
            total_tat += p[idx].tat;

            time_val = p[idx].ct;
            p[idx].completed = 1;
            done++;
        }
    }

    printf("\n\nPID\tAT\tBT\tPR\tWT\tTAT\tCT\n");

    for(int i = 0; i < n; i++) {
        printf("P%d\t%.2lf\t%.2lf\t%.2lf\t%.2lf\t%.2lf\t%.2lf\n",
               p[i].pid,
               p[i].at,
               p[i].bt,
               p[i].pr,
               p[i].wt,
               p[i].tat,
               p[i].ct);
    }

    printf("\nAverage Waiting Time = %.2lf", total_wt/n);
    printf("\nAverage Turnaround Time = %.2lf\n", total_tat/n);

    if (is_auto) {
        FILE *csv_file = fopen("Priority.csv", "w");
        if (csv_file != NULL) {
            fprintf(csv_file, "PID,Arrival_Time,Burst_Time,Completion_Time,Turnaround_Time,Waiting_Time\n");
            for(int i = 0; i < n; i++) {
                fprintf(csv_file, "%d,%.2lf,%.2lf,%.2lf,%.2lf,%.2lf\n",
                    p[i].pid, p[i].at, p[i].bt, p[i].ct, p[i].tat, p[i].wt);
            }
            fclose(csv_file);
            printf("\nData successfully exported to Priority.csv\n");
        } else {
            printf("\nWarning: Could not open Priority.csv for writing.\n");
        }
    }

    return 0;
}
