import tkinter as tk
from tkinter import messagebox
import json
import os


class ProcessInputApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduler Input")

        self.process_entries = []

        # Number of processes input
        tk.Label(root, text="Number of Processes:").grid(row=0, column=0, padx=10, pady=10)

        self.num_processes_entry = tk.Entry(root)
        self.num_processes_entry.grid(row=0, column=1)

        tk.Button(root, text="Create Inputs", command=self.create_inputs).grid(row=0, column=2, padx=10)

        self.input_frame = tk.Frame(root)
        self.input_frame.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Button(root, text="Submit", command=self.submit).grid(row=2, column=1, pady=10)

    def create_inputs(self):
        # Clear previous inputs
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        self.process_entries.clear()

        try:
            n = int(self.num_processes_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid integer")
            return

        # Headers
        tk.Label(self.input_frame, text="Process").grid(row=0, column=0, padx=5)
        tk.Label(self.input_frame, text="Arrival Time (AT)").grid(row=0, column=1, padx=5)
        tk.Label(self.input_frame, text="Burst Time (BT)").grid(row=0, column=2, padx=5)
        tk.Label(self.input_frame, text="Priority (PR)").grid(row=0, column=3, padx=5)

        # Create input rows
        for i in range(n):
            tk.Label(self.input_frame, text=f"P{i+1}").grid(row=i+1, column=0)

            at_entry = tk.Entry(self.input_frame, width=10)
            bt_entry = tk.Entry(self.input_frame, width=10)
            pr_entry = tk.Entry(self.input_frame, width=10)

            at_entry.grid(row=i+1, column=1)
            bt_entry.grid(row=i+1, column=2)
            pr_entry.grid(row=i+1, column=3)

            self.process_entries.append((at_entry, bt_entry, pr_entry))

    def submit(self):
        result = []

        try:
            for i, (at, bt, pr) in enumerate(self.process_entries):
                process_data = {
                    f"P{i+1}": {
                        "AT": int(at.get()),
                        "BT": int(bt.get()),
                        "PR": int(pr.get())
                    }
                }
                result.append(process_data)

        except ValueError:
            messagebox.showerror("Error", "All fields must be integers")
            return

        try:
            # Save to data.json in current directory
            file_path = os.path.join(os.getcwd(), "data.json")

            with open(file_path, "w") as f:
                json.dump(result, f, indent=4)

        except Exception as e:
            messagebox.showerror("File Error", str(e))
            return

        # Optional confirmation (quick feedback)
        # messagebox.showinfo("Success", "Data saved to data.json")

        # Close GUI
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessInputApp(root)
    root.mainloop()