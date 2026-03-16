#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX 100

typedef struct {
    int pid;
    double at, bt;
    double ct, wt, tat;
} Process;

void swap(Process *a, Process *b) {
    Process temp = *a;
    *a = *b;
    *b = temp;
}

int main(int argc, char *argv[]) {

    int n;
    Process p[MAX];
    double time_val = 0;
    double total_wt = 0, total_tat = 0;

    int gantt_pid[MAX];
    double gantt_time[MAX + 1];

    int is_auto = (argc == 1);

    if (is_auto) {
        n = 5;
        srand(time(NULL));
        for (int i = 0; i < n; i++) {
            p[i].pid = i + 1;
            p[i].at = rand() % 6;       // Arrival time: 0 to 5
            p[i].bt = (rand() % 10) + 1; // Burst time: 1 to 10
        }
        printf("Operating in Automatic Mode: Generating %d random processes...\n", n);
    } else {
        /* Validate number of processes */
        do {
            printf("Enter number of processes: ");
            scanf("%d", &n);
            if(n <= 0)
                printf("Invalid! Number of processes must be > 0.\n");
        } while(n <= 0);

        /* Input */
        for(int i = 0; i < n; i++) {

            p[i].pid = i + 1;

            printf("\nProcess P%d\n", i + 1);

            do {
                printf("Arrival Time: ");
                scanf("%lf", &p[i].at);
                if(p[i].at < 0)
                    printf("Invalid! Arrival Time cannot be negative.\n");
            } while(p[i].at < 0);

            do {
                printf("Burst Time: ");
                scanf("%lf", &p[i].bt);
                if(p[i].bt <= 0)
                    printf("Invalid! Burst Time must be > 0.\n");
            } while(p[i].bt <= 0);
        }
    }

    /* Sort by Arrival Time */
    for(int i = 0; i < n-1; i++)
        for(int j = 0; j < n-i-1; j++)
            if(p[j].at > p[j+1].at)
                swap(&p[j], &p[j+1]);

    /* FCFS Logic */
    for(int i = 0; i < n; i++) {

        if(time_val < p[i].at)
            time_val = p[i].at;

        gantt_pid[i] = p[i].pid;
        gantt_time[i] = time_val;

        p[i].ct = time_val + p[i].bt;
        p[i].tat = p[i].ct - p[i].at;
        p[i].wt = p[i].tat - p[i].bt;

        total_wt += p[i].wt;
        total_tat += p[i].tat;

        time_val = p[i].ct;
    }

    gantt_time[n] = time_val;

    /* Gantt Chart */
    printf("\n====== FCFS Scheduling ======\n\nGantt Chart:\n");

    for(int i = 0; i < n; i++)
        printf("|  P%d  ", gantt_pid[i]);
    printf("|\n");

    for(int i = 0; i <= n; i++)
        printf("%.2lf   ", gantt_time[i]);

    /* Output Table */
    printf("\n\nPID\tAT\tBT\tWT\tTAT\tCT\n");

    for(int i = 0; i < n; i++)
        printf("P%d\t%.2lf\t%.2lf\t%.2lf\t%.2lf\t%.2lf\n",
               p[i].pid, p[i].at, p[i].bt,
               p[i].wt, p[i].tat, p[i].ct);

    printf("\nAverage Waiting Time = %.2lf", total_wt/n);
    printf("\nAverage Turnaround Time = %.2lf\n", total_tat/n);

    if (is_auto) {
        FILE *csv_file = fopen("FCFS.csv", "w");
        if (csv_file != NULL) {
            fprintf(csv_file, "PID,Arrival_Time,Burst_Time,Completion_Time,Turnaround_Time,Waiting_Time\n");
            for(int i = 0; i < n; i++) {
                fprintf(csv_file, "%d,%.2lf,%.2lf,%.2lf,%.2lf,%.2lf\n",
                    p[i].pid, p[i].at, p[i].bt, p[i].ct, p[i].tat, p[i].wt);
            }
            fclose(csv_file);
            printf("\nData successfully exported to FCFS.csv\n");
        } else {
            printf("\nWarning: Could not open FCFS.csv for writing.\n");
        }
    }

    return 0;
}
