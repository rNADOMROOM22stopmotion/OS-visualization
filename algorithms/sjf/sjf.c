#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX 100
#define INF 1e9

typedef struct {
    int pid;
    double at, bt;
    double ct, wt, tat;
    int completed;
} Process;

int main(int argc, char *argv[]) {

    int n, done = 0;
    Process p[MAX];
    double time_val = 0;
    double total_wt = 0, total_tat = 0;

    int gantt_pid[MAX];
    double gantt_time[MAX + 1];
    int g = 0;
    
    int is_auto = (argc == 1);

    if (is_auto) {
        n = 5;
        srand(time(NULL));
        for (int i = 0; i < n; i++) {
            p[i].pid = i + 1;
            p[i].completed = 0;
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
            p[i].completed = 0;

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

    /* SJF Logic */
    while(done < n) {

        int idx = -1;
        double min_bt = INF;

        for(int i = 0; i < n; i++) {
            if(!p[i].completed && p[i].at <= time_val) {
                if(p[i].bt < min_bt) {
                    min_bt = p[i].bt;
                    idx = i;
                }
            }
        }

        if(idx == -1) {
            time_val++;
        }
        else {

            gantt_pid[g] = p[idx].pid;
            gantt_time[g] = time_val;
            g++;

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

    gantt_time[g] = time_val;

    /* Gantt Chart */
    printf("\n====== SJF Scheduling (Non-Preemptive) ======\n\nGantt Chart:\n");

    for(int i = 0; i < g; i++)
        printf("|  P%d  ", gantt_pid[i]);
    printf("|\n");

    for(int i = 0; i <= g; i++)
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
        FILE *csv_file = fopen("SJF.csv", "w");
        if (csv_file != NULL) {
            fprintf(csv_file, "PID,Arrival_Time,Burst_Time,Completion_Time,Turnaround_Time,Waiting_Time\n");
            for(int i = 0; i < n; i++) {
                fprintf(csv_file, "%d,%.2lf,%.2lf,%.2lf,%.2lf,%.2lf\n",
                    p[i].pid, p[i].at, p[i].bt, p[i].ct, p[i].tat, p[i].wt);
            }
            fclose(csv_file);
            printf("\nData successfully exported to SJF.csv\n");
        } else {
            printf("\nWarning: Could not open SJF.csv for writing.\n");
        }
    }

    return 0;
}
