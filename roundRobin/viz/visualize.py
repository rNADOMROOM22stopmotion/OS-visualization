import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Constants
CSV_FILE_PATH = '../round_robin_c/processes_data.csv'

def main():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: Could not find '{CSV_FILE_PATH}'.")
        print("Please ensure you have run the C program with the '--processes' flag first.")
        sys.exit(1)

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    if df.empty:
        print("The CSV file is empty. No data to visualize.")
        sys.exit(1)

    print(f"Data successfully loaded. Found {len(df)} processes.")

    # Chart 1: Turnaround Time & Waiting Time per Process
    plt.figure(figsize=(10, 6))
    width = 0.35
    x = range(len(df))
    
    plt.bar([i - width/2 for i in x], df['Turnaround_Time'], width, label='Turnaround Time', color='skyblue')
    plt.bar([i + width/2 for i in x], df['Waiting_Time'], width, label='Waiting Time', color='salmon')
    
    plt.xlabel('Process ID (PID)')
    plt.ylabel('Time Units')
    plt.title('Turnaround Time and Waiting Time per Process')
    plt.xticks(x, [f"P{pid}" for pid in df['PID']])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('tat_wt_chart.png')
    print("Saved 'tat_wt_chart.png'")
    
    # Chart 2: Burst Time vs Turnaround Time
    plt.figure(figsize=(10, 6))
    plt.scatter(df['Burst_Time'], df['Turnaround_Time'], color='purple', s=100, alpha=0.7)
    
    # Add labels to points
    for i, row in df.iterrows():
        plt.annotate(f"P{row['PID']}", 
                    (row['Burst_Time'], row['Turnaround_Time']),
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center')
                    
    plt.xlabel('Burst Time')
    plt.ylabel('Turnaround Time')
    plt.title('Relationship: Burst Time vs Turnaround Time')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('burst_vs_tat_scatter.png')
    print("Saved 'burst_vs_tat_scatter.png'")
    
    # Chart 3: Process Timeline (Arrival to Completion)
    plt.figure(figsize=(10, 6))
    
    for i, row in df.iterrows():
        plt.plot([row['Arrival_Time'], row['Completion_Time']], [i, i], 
                 marker='o', linewidth=3, markersize=8, label=f"P{row['PID']}")
                 
    plt.yticks(range(len(df)), [f"P{pid}" for pid in df['PID']])
    plt.xlabel('System Time')
    plt.title('Process Execution Lifespan (Arrival → Completion)')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.savefig('process_lifespan.png')
    print("Saved 'process_lifespan.png'")

    print("\nAll visualizations have been successfully generated!")

if __name__ == "__main__":
    main()
