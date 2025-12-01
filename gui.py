# gui.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from monitor import get_processes_info
import psutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque

class MemoryTrackerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Real-Time Memory Tracker")
        self.master.geometry("1000x700")

        self.process_list = []
        self.theme = "red"
        ctk.set_appearance_mode("Red")

        # Layout
        self.frame = ctk.CTkFrame(master)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="Memory Usage by Processes", font=("Arial", 20))
        self.label.pack(pady=10)

        # Search bar
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.frame, placeholder_text="Search by name or PID...", textvariable=self.search_var)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_process_list())

        # Table
        self.tree = ttk.Treeview(self.frame, columns=("PID", "Name", "Memory"), show='headings')
        self.tree.heading("PID", text="PID")
        self.tree.heading("Name", text="Process Name")
        self.tree.heading("Memory", text="Memory (MB)")
        self.tree.column("PID", width=100)
        self.tree.column("Name", width=500)
        self.tree.column("Memory", width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Button panel
        btn_frame = ctk.CTkFrame(self.frame)
        btn_frame.pack(pady=5)

        self.refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", command=self.update_process_list)
        self.refresh_btn.grid(row=0, column=0, padx=5)

        self.kill_btn = ctk.CTkButton(btn_frame, text="Kill Selected", command=self.kill_selected_process)
        self.kill_btn.grid(row=0, column=1, padx=5)

        self.theme_btn = ctk.CTkButton(btn_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=2, padx=5)

        # ======= GRAPH SETUP ========
        self.graph_frame = ctk.CTkFrame(self.frame)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.mem_usage = deque(maxlen=60)
        self.timestamps = deque(maxlen=60)

        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.line, = self.ax.plot([], [], color='cyan')
        self.ax.set_title("System RAM Usage Over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Used Memory (MB)")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Auto start updates
        self.update_process_list()
        self.update_graph()
        self.master.after(5000, self.auto_refresh)

    def update_process_list(self):
        search_text = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())

        self.process_list = get_processes_info()
        for proc in self.process_list:
            if (search_text in proc['name'].lower()) or (search_text in str(proc['pid'])):
                self.tree.insert("", "end", values=(proc['pid'], proc['name'], proc['memory']))

    def auto_refresh(self):
        self.update_process_list()
        self.master.after(5000, self.auto_refresh)

    def kill_selected_process(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a process to kill.")
            return

        pid = self.tree.item(selected[0])['values'][0]
        try:
            p = psutil.Process(pid)
            p.terminate()
            messagebox.showinfo("Success", f"Process {pid} terminated.")
            self.update_process_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_theme(self):
        if self.theme == "Red":
            ctk.set_appearance_mode("Red")
            self.theme = "Red"
        else:
            ctk.set_appearance_mode("Dark")
            self.theme = "dark"

    def update_graph(self):
        mem = psutil.virtual_memory()
        used_mb = (mem.total - mem.available) / (1024 * 1024)

        self.mem_usage.append(used_mb)
        self.timestamps.append(len(self.timestamps))  # Time tick as X-axis

        self.line.set_data(self.timestamps, self.mem_usage)
        self.ax.set_xlim(max(0, self.timestamps[0]), max(60, self.timestamps[-1] + 1))
        self.ax.set_ylim(0, mem.total / (1024 * 1024))  # Set max to total RAM

        self.canvas.draw()
        self.master.after(1000, self.update_graph)
