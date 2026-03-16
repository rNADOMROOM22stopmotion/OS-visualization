# OS CPU Scheduling Algorithm Visualizer

A comprehensive simulation and visualization tool for various Operating System CPU scheduling algorithms. This project implements core scheduling logic in C and provides powerful data visualization using Python, allowing users to analyze performance metrics through charts and an interactive dashboard.

## 🚀 Features

- **Multiple Algorithms Implemented:**
  - **FCFS** (First-Come, First-Served)
  - **Priority Scheduling** (Non-preemptive)
  - **Round Robin** (RR)
  - **SJF** (Shortest Job First)
  - **SRTF** (Shortest Remaining Time First)
- **Dual Operating Modes:**
  - **Manual Mode:** Input custom process details (Arrival Time, Burst Time, Priority).
  - **Automatic Mode:** Generate random processes for quick simulation and testing.
- **Rich Visualizations:**
  - Turnaround Time vs. Waiting Time per process.
  - Burst Time vs. Turnaround Time relationship analysis.
  - Process Execution Lifespan (Arrival to Completion) timeline.
- **Data Export:** All simulation results are exported to CSV for external analysis.
- **Interactive Dashboard:** A modern HTML/CSS interface to view and compare visualization results.

## 📂 Project Structure

```text
OS project/
├── algorithms/
│   ├── fcfs/             # C implementation of FCFS
│   ├── priority/         # C implementation of Priority Scheduling
│   ├── round_robin_c/    # C implementation of Round Robin
│   ├── sjf/              # C implementation of SJF
│   ├── srtf/             # C implementation of SRTF
│   └── viz/              # Python visualization scripts & Dashboard
│       ├── visualize_algo.py
│       └── index.html
├── screenshots/          # Project demonstration images
├── pyproject.toml        # Python project configuration
└── reqirements.txt       # Python dependencies
```

## 🛠️ Setup & Usage

### 1. Prerequisites
- GCC Compiler (for C programs)
- Python 3.10+
- pip (Python package manager)

### 2. Install Dependencies
```bash
pip install -r reqirements.txt
```

### 3. Running a Simulation
1. Navigate to an algorithm directory (e.g., `algorithms/fcfs/`).
2. Compile the C program:
   ```bash
   gcc fcfs.c -o fcfs
   ```
3. Run the program:
   - **Automatic Mode:** `./fcfs` (Generates random data and `FCFS.csv`)
   - **Manual Mode:** (Follow on-screen prompts if implemented)

### 4. Generating Visualizations
1. Navigate to the `algorithms/viz/` directory.
2. Run the visualization script:
   ```bash
   python visualize_algo.py
   ```
3. Select the algorithm you just ran. The script will read the generated CSV and save charts in the respective algorithm folder (e.g., `viz/FCFS/`).

### 5. Viewing the Dashboard
Open `algorithms/viz/index.html` in any modern web browser to view the generated charts in an interactive layout.

## 📊 Sample Visualizations
The tool generates several insights:
- **TAT & WT Chart:** Compare how long processes wait vs. their total turnaround time.
- **Burst vs TAT Scatter:** Analyze how process length affects completion time.
- **Process Lifespan:** A timeline view of when each process arrived and finished.

## 👥 Credits

This project was developed by:
- **Dhruv Rathod**
- **Aagam Gopani**
- **Dev Lakhani**

---
*Created as part of the Operating Systems Course Project.*
