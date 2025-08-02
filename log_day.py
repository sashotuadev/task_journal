#!/usr/bin/env python3
#._core_ops/scripts/log_day.py

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import csv
import os
import datetime

STATUS_LIST = [
    "PENDING",
    "QUEUED",
    "ACTIVE",
    "DONE",
    "DROPPED",
    "FAILED"
]

DEADLINE_LEVELS = [
    "URGENT (immediat)",
    "Prioritaire (sous 3 jours)",
    "Normal (cette semaine)",
    "Souple (ce mois ci)"
]

DEADLINE_COLORS = {
    "URGENT (immediat)": "red",
    "Prioritaire (sous 3 jours)": "purple",
    "Normal (cette semaine)": "green",
    "Souple (ce mois ci)": "blue"
}

FIELDNAMES = ["date", "time", "type", "content", "status", "email", "phone", "deadline"]

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs/")
os.makedirs(BASE_PATH, exist_ok=True)
TODAY = datetime.date.today().isoformat()
FILENAME = os.path.join(BASE_PATH, f"log_{TODAY}.csv")

class LogApp:
    def __init__(self, root):
        self.root = root
        root.title("** Journal de Tâches **")

        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        tk.Label(self.left_frame, text="Tâches du jour (PENDING, QUEUED, ACTIVE):").pack()
        self.task_listbox = tk.Listbox(self.left_frame, width=60,)
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        self.task_listbox.bind("<Double-Button-1>", self.modify_status)

        now = datetime.datetime.now()
        self.date = tk.StringVar(value=TODAY)
        self.time = tk.StringVar(value=now.strftime("%H:%M:%S"))
        self.type = tk.StringVar()
        self.content = tk.Text(self.right_frame, height=5, width=40)
        self.status = tk.StringVar(value="PENDING")
        self.email = tk.StringVar()
        self.phone = tk.StringVar()
        self.deadline = tk.StringVar(value=DEADLINE_LEVELS[0])

        ttk.Label(self.right_frame, text=f"Date: {TODAY}").pack(anchor='w')

        ttk.Label(self.right_frame, text=f"Heure: {now.strftime('%H:%M:%S')}").pack(anchor='w')

        ttk.Label(self.right_frame, text="Type de tâche:").pack(anchor='w')
        ttk.Entry(self.right_frame, textvariable=self.type).pack(fill=tk.X)

        ttk.Label(self.right_frame, text="Contenu:").pack(anchor='w')
        self.content.pack()

        ttk.Label(self.right_frame, text="Status:").pack(anchor='w')
        ttk.Combobox(self.right_frame, textvariable=self.status, values=STATUS_LIST).pack(fill=tk.X)

        ttk.Label(self.right_frame, text="Email:").pack(anchor='w')
        ttk.Entry(self.right_frame, textvariable=self.email).pack(fill=tk.X)

        ttk.Label(self.right_frame, text="Téléphone:").pack(anchor='w')
        ttk.Entry(self.right_frame, textvariable=self.phone).pack(fill=tk.X)

        ttk.Label(self.right_frame, text="Deadline:").pack(anchor='w')
        ttk.Combobox(self.right_frame, textvariable=self.deadline, values=DEADLINE_LEVELS).pack(fill=tk.X)

        ttk.Button(self.right_frame, text="Enregistrer", command=self.confirm_entry).pack(pady=10)
        self.load_tasks()
        footer = tk.Label(self.right_frame, text="© DEV_SASHOTUA - BUILT/001 - 2 Août 2025 - Licences GPL GNU v3", font=("Arial", 8), fg="black")
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=2)

    def confirm_entry(self):
        data={
            "date": self.date.get(),
            "time": self.time.get(),
            "type": self.type.get(),
            "content": self.content.get("1.0", tk.END).strip(),
            "status": self.status.get(),
            "email": self.email.get(),
            "phone": self.phone.get(),
            "deadline": self.deadline.get()
        }
        summary = f"Tâche: {data['type']} \nContenu: {data['content']}\nStatut: {data['status']}\nEmail: {data['email']}\nTél: {data['phone']}\nDeadline: {data['deadline']}"
        if messagebox.askyesno("Confirmer l'Enregistrement", summary):
            self.save_entry(data)
            self.clear_form()
            self.load_tasks()

    def save_entry(self, data):
        file_exists = os.path.isfile(FILENAME)
        with open(FILENAME, "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def clear_form(self):
        self.type.set("")
        self.content.delete("1.0",tk.END)
        self.status.set("PENDING")
        self.email.set("")
        self.phone.set("")
        self.deadline.set(DEADLINE_LEVELS[0])

    def load_tasks(self):
        self.task_listbox.delete(0, tk.END)
        if not os.path.isfile(FILENAME):
            return

        grouped = {}

        with open(FILENAME, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['status'] in ["PENDING", "QUEUED", "ACTIVE"]:
                    date = row['date']
                    grouped.setdefault(date, []).append(row)

            for date in sorted(grouped.keys()):
                    header = f"** {date} **"
                    self.task_listbox.insert(tk.END, header)
                    self.task_listbox.itemconfig(tk.END, {'fg': 'black'})

            for row in grouped[date]:
                    phone = row.get("phone", "-")
                    mail = row.get("email", "-")
                    content_preview = row.get("content", "") [:400]
                    line = f"[{row['status']}] {row['type']} - {phone} - {mail} - {content_preview} "
                    self.task_listbox.insert(tk.END, line)
                    self.task_listbox.itemconfig(tk.END, {'fg': DEADLINE_COLORS.get(row.get('deadline'), 'black')})

    def modify_status(self, event):
        idx = self.task_listbox.curselection()
        if not idx:
            return
        status_win = tk.Toplevel(self.root)
        status_win.title("Modifier le statut")

        tk.Label(status_win, text="Choisir le nouveau statut :").pack(pady=5)

        status_var = tk.StringVar(value="PENDING")
        for s in STATUS_LIST:
            tk.Radiobutton(status_win, text=s, variable=status_var, value=s).pack(anchor="w")

        def apply_status():
            new_status = status_var.get()
            row = []
            with open(FILENAME, newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            selected_text = self.task_listbox.get(idx)
            for row in rows:
                if row['status'] in ["PENDING", "QUEUED", "ACTIVE"] and row['content'][:400] in selected_text:
                    row['status'] = new_status
                    break
            with open(FILENAME, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)

            status_win.destroy()
            self.load_tasks()

        tk.Button(status_win, text="Valider", command=apply_status).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogApp(root)
    root.mainloop()



