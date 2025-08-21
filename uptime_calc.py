import subprocess
import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def get_dates(days):
    dates = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%b %e").strip()
        dates.append(date)
    return dates

def get_last_output():
    result = subprocess.run(['last', '-x'], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Error running 'last -x'")
    return result.stdout

def extract_durations(output, dates):
    durations = {date: [] for date in dates}
    pattern = re.compile(r"reboot\s+system boot.*(" +
                         "|".join(re.escape(d) for d in dates) +
                         r").*\((\d{2}):(\d{2})\)")

    for line in output.splitlines():
        if "still running" in line:
            continue
        match = pattern.search(line)
        if match:
            date_str = match.group(1).strip()
            h = int(match.group(2))
            m = int(match.group(3))
            total_minutes = h * 60 + m
            if date_str in durations:
                durations[date_str].append(total_minutes)
    return durations

def sum_minutes(minutes_list):
    return sum(minutes_list)

def format_minutes_verbose(total_minutes):
    h = total_minutes // 60
    m = total_minutes % 60
    parts = []
    if h > 0:
        parts.append(f"{h} hr{'s' if h > 1 else ''}")
    if m > 0:
        parts.append(f"{m} min{'s' if m > 1 else ''}")
    if not parts:  # If 0 mins uptime
        parts.append("0 mins")
    return " and ".join(parts)

class UptimeApp:
    def __init__(self, root):
        self.root = root
        root.title("System Uptime Calculator")
        root.geometry("700x600")

        # Create a canvas and scrollbar for scrolling content
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Enable mousewheel/touchpad scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)      # Windows and macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)        # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)        # Linux scroll down

        # Widgets inside scrollable frame
        ttk.Label(self.scrollable_frame, text="Calculate uptime for past:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=(10, 2))

        self.choice_var = tk.StringVar(value="1")
        ttk.Radiobutton(self.scrollable_frame, text="1 Day", variable=self.choice_var, value="1").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(self.scrollable_frame, text="7 Days (Week)", variable=self.choice_var, value="7").grid(row=2, column=0, sticky=tk.W)

        self.calc_button = ttk.Button(self.scrollable_frame, text="Calculate", command=self.calculate)
        self.calc_button.grid(row=3, column=0, pady=10, sticky=tk.W)

        self.single_output = ttk.Label(self.scrollable_frame, text="", font=("Arial", 12))
        self.single_output.grid(row=4, column=0, pady=10, sticky=tk.W)

        self.tree = None
        self.summary_label = None
        self.plot_canvas = None

        self.export_button = ttk.Button(self.scrollable_frame, text="Export Report", command=self.export_report, state=tk.DISABLED)
        self.export_button.grid(row=99, column=0, sticky=tk.W, pady=10)

        self.latest_report_text = ""

    def _on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows / macOS
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def calculate(self):
        days = int(self.choice_var.get())
        try:
            dates = get_dates(days)
            last_output = get_last_output()
            durations = extract_durations(last_output, dates)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.latest_report_text = ""
        self.single_output.config(text="")
        if self.tree:
            self.tree.destroy()
            self.tree = None
        if self.summary_label:
            self.summary_label.destroy()
            self.summary_label = None
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
            self.plot_canvas = None
        self.export_button.config(state=tk.DISABLED)

        if days == 1:
            day = dates[0]
            total = sum_minutes(durations.get(day, []))
            text = f"Total uptime in past 1 day ({day}): {format_minutes_verbose(total)}"
            self.single_output.config(text=text)
            self.latest_report_text = text
        else:
            self.show_week_output(durations, dates)
            self.export_button.config(state=tk.NORMAL)

    def show_week_output(self, durations, dates):
        if self.tree:
            self.tree.destroy()
        if self.summary_label:
            self.summary_label.destroy()

        self.tree = ttk.Treeview(self.scrollable_frame, columns=("Date", "Uptime"), show="headings", height=7)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Uptime", text="Uptime")
        self.tree.column("Date", width=120, anchor=tk.CENTER)
        self.tree.column("Uptime", width=160, anchor=tk.CENTER)
        self.tree.grid(row=5, column=0, pady=(10, 5), sticky="ew")

        dates_reversed = list(reversed(dates))  # Oldest to newest
        total_week = 0
        daily_totals = []

        for date in dates_reversed:
            total = sum_minutes(durations.get(date, []))
            formatted = format_minutes_verbose(total)
            self.tree.insert("", tk.END, values=(date, formatted))
            total_week += total
            daily_totals.append((date, total))

        avg_daily = total_week / len(dates)
        max_day = max(daily_totals, key=lambda x: x[1])
        min_day = min(daily_totals, key=lambda x: x[1])

        summary_text = (
            f"Total uptime in past 7 days: {format_minutes_verbose(total_week)}\n"
            f"Average daily uptime: {format_minutes_verbose(int(avg_daily))}\n"
            f"Max uptime: {max_day[0]} with {format_minutes_verbose(max_day[1])}\n"
            f"Min uptime: {min_day[0]} with {format_minutes_verbose(min_day[1])}\n"
        )
        self.latest_report_text = "Uptime per day for past 7 days:\n"
        for date, total in daily_totals:
            self.latest_report_text += f"{date}: {format_minutes_verbose(total)}\n"
        self.latest_report_text += summary_text

        self.summary_label = ttk.Label(self.scrollable_frame, text=summary_text, font=("Arial", 11), justify=tk.LEFT)
        self.summary_label.grid(row=6, column=0, sticky=tk.W, pady=(5, 15))

        self.plot_week_uptime(daily_totals)

    def plot_week_uptime(self, daily_totals):
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()

        dates, totals = zip(*daily_totals)
        totals_hours = [t / 60 for t in totals]

        colors = []
        for h in totals_hours:
            if h < 3:
                colors.append('red')
            elif h < 6:
                colors.append('orange')
            else:
                colors.append('green')

        fig, ax = plt.subplots(figsize=(7, 3))
        bars = ax.bar(dates, totals_hours, color=colors)
        ax.set_ylabel('Uptime (hours)')
        ax.set_title('System Uptime per Day (Past 7 Days)')
        plt.xticks(rotation=45)
        plt.tight_layout()

        import matplotlib.patches as mpatches
        red_patch = mpatches.Patch(color='red', label='< 3 hours (Low uptime)')
        orange_patch = mpatches.Patch(color='orange', label='3 - 6 hours (Moderate uptime)')
        green_patch = mpatches.Patch(color='green', label='> 6 hours (High uptime)')
        ax.legend(handles=[red_patch, orange_patch, green_patch])

        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(row=7, column=0, pady=10)

    def export_report(self):
        if not self.latest_report_text:
            messagebox.showinfo("No data", "Nothing to export.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                                            title="Save uptime report")
        if file:
            try:
                with open(file, "w") as f:
                    f.write(self.latest_report_text)
                messagebox.showinfo("Success", f"Report saved to {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UptimeApp(root)
    root.mainloop()

