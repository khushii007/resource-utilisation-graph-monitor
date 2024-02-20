# Import necessary libraries/modules
import psutil  # Library for system monitoring
import socket  # Library for network-related functions
import tkinter as tk  # GUI library
from tkinter import ttk  # Themed Tkinter widgets
from tkinter import messagebox  # Message box dialogs in Tkinter
import matplotlib.pyplot as plt  # Plotting library
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Matplotlib integration with Tkinter

# Function to toggle the visibility of the task manager window
def toggle_task_manager():
    if task_manager.winfo_ismapped():
        task_manager.withdraw()  # Hide the window
    else:
        task_manager.deiconify()  # Show the window

def update_process_list():
    # Clear previous data in the tree (GUI component)
    tree.delete(*tree.get_children())

    # Get a list of currently running processes
    process_list = psutil.process_iter()

    # Iterate over each process in the list
    for idx, proc in enumerate(process_list):
        try:
            # Extract process information
            pid = proc.pid
            app_name = proc.name()
            memory_info = f"{proc.memory_info().rss / (1024 * 1024 * 1024):.2f} GB"
            
            # Extract CPU usage information for each core
            cpu_info = ", ".join([f"Core {idx + 1}: {util}%" for idx, util in enumerate(psutil.cpu_percent(percpu=True))])
            
            # Extract disk usage information
            disk_info = f"{psutil.disk_usage('/').percent}%"

            # Insert the extracted process information into the task manager table (GUI component)
            tree.insert("", "end", values=(pid, app_name, memory_info, cpu_info, disk_info))
        
        # Handle exceptions for specific process-related errors
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Schedule the function to run again after 2000 milliseconds (2 seconds)
    root.after(2000, update_process_list)


# Function to update the utilization graph
def update_utilization_graph():
    # Gather system resource utilization data
    memory_usage.append(psutil.virtual_memory().percent)
    cpu_usage.append(sum(psutil.cpu_percent(percpu=True)) / psutil.cpu_count())
    disk_usage.append(psutil.disk_usage('/').percent)

    if len(memory_usage) > 30:  # Display the last 30 data points
        memory_usage.pop(0)
        cpu_usage.pop(0)
        disk_usage.pop(0)

    # Update the utilization graph
    ax.clear()
    ax.plot(memory_usage, label='Memory')
    ax.plot(cpu_usage, label='Average CPU')
    ax.plot(disk_usage, label='Disk')
    ax.legend()
    ax.set_xlabel('Time')
    ax.set_ylabel('Utilization (%)')
    canvas.draw()

    root.after(1000, update_utilization_graph)  # Update every 1 second

# Function to close the network information window
def close_network_info():
    network_info_window.destroy()

# Function to show network information in a separate window


# Function to show network information in a separate window
def show_network_info():
    try:
        global network_info_window  # Declare a global variable to track the network information window
        network_info_window = tk.Toplevel(root)  # Create a new Toplevel window (sub-window) for network information
        network_info_window.title("Network Information")  # Set the title of the network information window

        network_info_text = tk.Text(network_info_window, height=20, width=60)  # Create a Text widget for displaying network information
        network_info_text.pack(padx=20, pady=20)  # Pack the Text widget into the window with padding

        network_info = ""  # Initialize an empty string to store network information
        interfaces = psutil.net_if_addrs()  # Get network interface addresses using psutil
        for interface_name, interface_addresses in interfaces.items():
            network_info += f"Interface: {interface_name}\n"
            for addr in interface_addresses:
                if addr.family == socket.AF_INET:
                    network_info += f"  IP Address: {addr.address}\n"
                    network_info += f"  Netmask: {addr.netmask}\n"
                elif addr.family == socket.AF_INET6:
                    network_info += f"  IPv6 Address: {addr.address}\n"
                    network_info += f"  Netmask: {addr.netmask}\n"
            network_info += "\n"

        network_speed = psutil.net_if_stats()  # Get network interface statistics
        network_info += "Network Speed:\n"
        for interface_name, stats in network_speed.items():
            network_info += f"  Interface: {interface_name}\n"
            network_info += f"  Speed: {stats.speed} Mbps\n"
            network_info += "\n"

        network_info_text.insert(tk.END, network_info)  # Insert the collected network information into the Text widget

        close_button = ttk.Button(
            network_info_window, text="Close", command=close_network_info)  # Create a button to close the network information window
        close_button.pack(pady=10)  # Pack the close button into the network information window
    except Exception as e:
        # Handle exceptions by displaying an error message box with the details of the error
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Function to show battery and bluetooth information


def show_battery_and_bluetooth():
    try:
        battery_info = f"Battery Percentage: {
            psutil.sensors_battery().percent}%\n"
        battery_info += f"Power Plugged: {
            psutil.sensors_battery().power_plugged}\n\n"
        messagebox.showinfo("Battery & Bluetooth Info", f"{
                            battery_info}\n")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def show_disk_info():
    try:
        disk_info_window = tk.Toplevel(root)
        disk_info_window.title("Disk Information")

        disk_info_text = tk.Text(disk_info_window, height=20, width=60)
        disk_info_text.pack(padx=20, pady=20)

        disk_info = ""
        partitions = psutil.disk_partitions()
        for partition in partitions:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            disk_info += f"Drive: {partition.device}\n"
            disk_info += f"Mountpoint: {partition.mountpoint}\n"
            disk_info += f"File System Type: {partition.fstype}\n"
            disk_info += f"Total Size: {disk_usage.total /
                                        (1024 * 1024 * 1024):.2f} GB\n"
            disk_info += f"Used: {disk_usage.used /
                                  (1024 * 1024 * 1024):.2f} GB\n"
            disk_info += f"Free: {disk_usage.free /
                                  (1024 * 1024 * 1024):.2f} GB\n"
            disk_info += f"Percentage Used: {disk_usage.percent}%\n\n"

        disk_info_text.insert(tk.END, disk_info)

        close_button = ttk.Button(
            disk_info_window, text="Close", command=disk_info_window.destroy)
        close_button.pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Main window
root = tk.Tk()
root.title("Task Manager with Utilization Graph")

# Styling
style = ttk.Style()
style.theme_use('clam')

# Frame to contain buttons
button_frame = ttk.Frame(root)
button_frame.pack()

# Button to toggle task manager view
task_manager_button = ttk.Button(
    button_frame, text="Toggle Task Manager", command=toggle_task_manager)
task_manager_button.pack(side=tk.LEFT, padx=5, pady=10)

# Button to show network information
network_button = ttk.Button(
    button_frame, text="Show Network Info", command=show_network_info)
network_button.pack(side=tk.LEFT, padx=5, pady=10)

# Button to show battery and Bluetooth information
battery_bluetooth_button = ttk.Button(
    button_frame, text="Show Battery", command=show_battery_and_bluetooth)
battery_bluetooth_button.pack(side=tk.LEFT, padx=5, pady=10)

# Button to show disk information

disk_button = ttk.Button(
    button_frame, text="Show Disk Info", command=show_disk_info)
disk_button.pack(side=tk.LEFT, padx=5, pady=10)

# Creating a Toplevel window for the task manager table
task_manager = tk.Toplevel(root)
task_manager.title("Task Manager")
task_manager.geometry("700x400")

# Creating a frame for the task manager table
tree_frame = ttk.Frame(task_manager)

# Creating a treeview to display the process information
tree = ttk.Treeview(tree_frame, columns=(
    "PID", "App Name", "Memory Utilization", "CPU Utilization", "Disk Utilization"))
tree.heading("#0", text="Process ID")
tree.heading("#1", text="App Name")
tree.heading("#2", text="Memory Utilization")
tree.heading("#3", text="CPU Utilization")
tree.heading("#4", text="Disk Utilization")
tree.pack(expand=True, fill=tk.BOTH)

tree_frame.pack(expand=True, fill=tk.BOTH)

# Creating a frame for the utilization graph
graph_frame = ttk.Frame(root)
graph_frame.pack(padx=20, pady=10)

fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

memory_usage, cpu_usage, disk_usage = [], [], []

# Start gathering and displaying process information
update_process_list()
update_utilization_graph()

# Run the application
root.mainloop()
