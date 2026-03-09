import tkinter as tk
import threading
import time

# Global state
agent_running = False
current_task = "Idle"


def start_agent():

    global agent_running
    agent_running = True

    thread = threading.Thread(target=agent_loop)
    thread.start()


def stop_agent():

    global agent_running
    agent_running = False
    status_label.config(text="Stopped")


def agent_loop():

    global agent_running

    while agent_running:

        task = task_entry.get()

        if task != "":
            status_label.config(text="Running task...")
            task_label.config(text=task)

            # simulate work
            time.sleep(3)

            status_label.config(text="Task completed")

        time.sleep(1)


def send_task():

    task = task_entry.get()
    task_label.config(text=task)
    status_label.config(text="Task queued")


# GUI Window
root = tk.Tk()
root.title("Visual AI Agent")
root.geometry("400x300")

title = tk.Label(root, text="Offline Visual AI Agent", font=("Arial",16))
title.pack(pady=10)

task_entry = tk.Entry(root, width=40)
task_entry.pack(pady=5)

send_button = tk.Button(root, text="Send Task", command=send_task)
send_button.pack(pady=5)

start_button = tk.Button(root, text="Start Agent", command=start_agent)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Agent", command=stop_agent)
stop_button.pack(pady=5)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack(pady=10)

task_label = tk.Label(root, text="Current Task: None")
task_label.pack(pady=5)

root.mainloop()