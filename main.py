import json
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, scrolledtext

class SleepCycleTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Sleep Cycle Tracker")
        self.root.geometry("400x500")
        self.data_file = "sleep_data.json"
        self.data = self.load_data()
        tk.Label(root, text="Sleep Cycle Tracker").pack(pady=10)
        buttons = [
            ("Add Sleep Time", self.add_sleep_time),
            ("Add Wake Time", self.add_wake_time),
            ("View Average Sleep", self.view_average_sleep),
            ("View history", self.view_history),
        ]
        for text, cmd in buttons:
            tk.Button(root, text=text, command=cmd, width=20, height=2).pack(pady=5)
        self.result_label = tk.Label(root, text="", wraplength=350, font=("Times New Roman", 12), fg="blue")
        self.result_label.pack(pady=10)

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.data, f)

    def get_time_input(self, title):
        time_input = [None]
        def use_now():
            time_entry.delete(0, tk.END)
            time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        def submit():
            try:
                time_input[0] = datetime.strptime(time_entry.get(), "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M")
                time_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid format. Use YYYY-MM-DD HH:MM.")
        time_window = tk.Toplevel(self.root)
        time_window.title(title)
        time_window.geometry("300x150")
        tk.Label(time_window, text=f"Enter {title.lower()} (YYYY-MM-DD HH:MM):").pack(pady=5)
        time_entry = tk.Entry(time_window, width=25)
        time_entry.pack(pady=5)
        tk.Button(time_window, text="Now", command=use_now).pack(side="left", padx=10, pady=10)
        tk.Button(time_window, text="Submit", command=submit).pack(side="right", padx=10, pady=10)
        time_window.grab_set()
        self.root.wait_window(time_window)
        return time_input[0]

    def add_sleep_time(self):
        sleep_time = self.get_time_input("Sleep Time")
        if sleep_time:
            date = sleep_time.split(" ")[0]
            for entry in self.data:
                if entry["date"] == date:
                    entry.setdefault("sleep_wake_pairs", []).append({"sleep_time": sleep_time})
                    break
            else:
                self.data.append({"date": date, "sleep_wake_pairs": [{"sleep_time": sleep_time}]})
            self.save_data()
            messagebox.showinfo("Success", f"Sleep time logged: {sleep_time}")

    def add_wake_time(self):
        wake_time = self.get_time_input("Wake Time")
        if wake_time:
            wake_date = datetime.strptime(wake_time.split(" ")[0], "%Y-%m-%d")
            wake_time_dt = datetime.strptime(wake_time, "%Y-%m-%d %H:%M")
            for entry in self.data:
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
                if wake_date == entry_date or wake_date == entry_date + timedelta(days=1):
                    for pair in reversed(entry["sleep_wake_pairs"]):
                        if "wake_time" not in pair:
                            sleep_time = datetime.strptime(pair["sleep_time"], "%Y-%m-%d %H:%M")
                            if wake_time_dt < sleep_time:
                                wake_time_dt += timedelta(days=1)
                            pair["wake_time"] = wake_time_dt.strftime("%Y-%m-%d %H:%M")
                            self.save_data()
                            messagebox.showinfo("Success", f"Wake time logged: {pair['wake_time']}")
                            return
            messagebox.showerror("Error", "No unmatched sleep time found for the selected date.")

    def calculate_avg(self, period):
        now = datetime.now()
        period_map = {
            'month': now - timedelta(days=31),
            'week': now - timedelta(days=8),
            'all': datetime.min
        }
        if period in period_map:
            start_date = period_map[period]
            end_date = now
        elif period == 'manual':
            start_date = self.get_time_input("Start Date")
            end_date = self.get_time_input("End Date")
            if not (start_date and end_date):
                return
            start_date = datetime.strptime(start_date.split(" ")[0], "%Y-%m-%d")
            end_date = datetime.strptime(end_date.split(" ")[0], "%Y-%m-%d")
        filtered_data = [
            entry for entry in self.data
            if start_date <= datetime.strptime(entry['date'], "%Y-%m-%d") <= end_date
        ]
        durations = []
        for entry in filtered_data:
            for pair in entry.get("sleep_wake_pairs", []):
                if "wake_time" in pair:
                    sleep_time = datetime.strptime(pair["sleep_time"], "%Y-%m-%d %H:%M")
                    wake_time = datetime.strptime(pair["wake_time"], "%Y-%m-%d %H:%M")
                    if wake_time < sleep_time:
                        wake_time += timedelta(days=1)
                    durations.append((wake_time - sleep_time).total_seconds() / 3600)
        if durations:
            avg_sleep = sum(durations) / len(durations)
            hours, minutes = divmod(avg_sleep * 60, 60)
            self.result_label.config(text=f"Average Sleep: {int(hours)} hours {int(minutes)} minutes")
            self.plot_sleep_data(filtered_data)
        else:
            self.result_label.config(text="No data available for the selected period.")

    def view_average_sleep(self):
        avg_window = tk.Toplevel(self.root)
        avg_window.title("Select Average Period")
        avg_window.geometry("300x200")
        periods = [
            ("Last Month", 'month'),
            ("Last Week", 'week'),
            ("All Data", 'all'),
            ("Manual Input", 'manual')
        ]
        for text, period in periods:
            tk.Button(avg_window, text=text, command=lambda p=period: self.calculate_avg(p)).pack(pady=5)

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Sleep history")
        history_window.geometry("400x500")
        available_months = sorted({entry["date"][:7] for entry in self.data})
        selected_month = tk.StringVar(value="Select Month")
        def update_history():
            if selected_month.get() == "Select Month":
                messagebox.showwarning("Warning", "Please select a month.")
                return
            sorted_data = sorted(
                [entry for entry in self.data if entry["date"].startswith(selected_month.get())],
                key=lambda x: x["date"]
            )
            history = "\n".join(
                f"{entry['date']}\n" + "\n".join(
                    f"    {pair.get('sleep_time', 'No Sleep Time')} - {pair.get('wake_time', 'No Wake Time')}"
                    for pair in entry["sleep_wake_pairs"]
                )
                for entry in sorted_data
            )
            scrolled.config(state=tk.NORMAL)
            scrolled.delete(1.0, tk.END)
            scrolled.insert(tk.END, history or "No data available for the selected month.")
            scrolled.config(state=tk.DISABLED)
        def delete_entry():
            if selected_month.get() == "Select Month":
                messagebox.showwarning("Warning", "Please select a month to delete entries.")
                return
            selected_text = scrolled.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if not selected_text:
                messagebox.showwarning("Warning", "Please select an entry to delete.")
                return
            for entry in self.data:
                if entry["date"] in selected_text:
                    self.data.remove(entry)
                    self.save_data()
                    update_history()
                    messagebox.showinfo("Info", "Entry deleted successfully.")
                    return
            messagebox.showerror("Error", "Could not find the selected entry.")
        tk.Label(history_window, text="Select a month:").pack(pady=5)
        tk.OptionMenu(history_window, selected_month, *available_months).pack(pady=5)
        tk.Button(history_window, text="Show history", command=update_history).pack(pady=10)
        scrolled = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, width=50, height=15)
        scrolled.pack(pady=10, padx=10)
        scrolled.config(state=tk.DISABLED)
        tk.Button(history_window, text="Delete Selected", command=delete_entry).pack(pady=10)

    def plot_sleep_data(self, filtered_data):
        durations_by_day = {}
        for entry in filtered_data:
            for pair in entry["sleep_wake_pairs"]:
                if "wake_time" in pair:
                    sleep_time = datetime.strptime(pair["sleep_time"], "%Y-%m-%d %H:%M")
                    wake_time = datetime.strptime(pair["wake_time"], "%Y-%m-%d %H:%M")
                    if wake_time < sleep_time:
                        wake_time += timedelta(days=1)
                    while sleep_time.date() < wake_time.date():
                        end_of_day = datetime.combine(sleep_time.date(), datetime.max.time())
                        duration = (end_of_day - sleep_time).total_seconds() / 3600
                        if duration >= 2:
                            durations_by_day.setdefault(sleep_time.date(), []).append(duration)
                        sleep_time = datetime.combine(sleep_time.date() + timedelta(days=1), datetime.min.time())
                    duration = (wake_time - sleep_time).total_seconds() / 3600
                    if duration >= 2:
                        durations_by_day.setdefault(sleep_time.date(), []).append(duration)
        total_durations_by_day = {
            date: sum(durations) for date, durations in durations_by_day.items()
        }
        dates = sorted(total_durations_by_day.keys())
        durations = [total_durations_by_day[date] for date in dates]
        if dates and durations:
            plot_window = tk.Toplevel(self.root)
            plot_window.title("Sleep Duration Over Time")
            plot_window.geometry("600x400")
            canvas = tk.Canvas(plot_window, width=580, height=360, bg="white")
            canvas.pack(pady=10)
            margin = 50
            width = 580 - margin * 2
            height = 360 - margin * 2
            max_duration = max(durations)
            min_duration = min(durations)
            duration_range = max_duration - min_duration or 1
            canvas.create_line(margin, height + margin, margin, margin, arrow=tk.LAST)
            canvas.create_line(margin, height + margin, width + margin, height + margin, arrow=tk.LAST)
            step_x = width / (len(dates) - 1 if len(dates) > 1 else 1)
            prev_x, prev_y = None, None
            for i, date in enumerate(dates):
                x = margin + i * step_x
                y = height + margin - ((durations[i] - min_duration) / duration_range) * height
                canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")
                if prev_x is not None and prev_y is not None:
                    canvas.create_line(prev_x, prev_y, x, y, fill="blue")
                prev_x, prev_y = x, y
                if i % max(1, len(dates) // 10) == 0:
                    canvas.create_text(x, height + margin + 15, text=date.strftime("%Y-%m-%d"), angle=45, anchor=tk.NW)
            canvas.create_text(margin - 10, margin, text=f"{max_duration:.1f}h", anchor=tk.E)
            canvas.create_text(margin - 10, height + margin, text=f"{min_duration:.1f}h", anchor=tk.E)
        else:
            messagebox.showerror("Error", "No sleep data to plot.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SleepCycleTracker(root)
    root.mainloop()
