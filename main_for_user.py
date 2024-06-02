import tkinter as tk
from tkinter import ttk, messagebox

# Example choices for DCOP type and Algorithm
dcop_types = ["Type1", "Type2", "Type3"]
algorithms = ["Algorithm1", "Algorithm2", "Algorithm3"]

# Global variables to store user's input
dcop_type_var = None
algorithm_var = None
agents_scale = None
seed_entry = None

user_dcop_type = None
user_amount_agents = None
user_seed_number = None
user_algorithm = None


def initialize_shared_variables(root):
    global dcop_type_var, algorithm_var, agents_scale, seed_entry
    dcop_type_var = tk.StringVar(value=dcop_types[0])
    algorithm_var = tk.StringVar(value=algorithms[0])
    agents_scale = tk.Scale(root, from_=3, to=50, orient=tk.HORIZONTAL)
    seed_entry = tk.Entry(root)
    seed_entry.insert(0, "0")  # Set default value to 0


def create_main_window():
    root = tk.Tk()
    root.title("DCOP Configuration")
    initialize_shared_variables(root)
    add_dcop_type_section(root)
    add_amount_agents_section(root)
    add_seed_number_section(root)
    add_algorithm_section(root)
    add_submit_button(root)

    return root


def add_dcop_type_section(root):
    global dcop_type_var
    tk.Label(root, text="Type of DCOP:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    dcop_type_menu = ttk.Combobox(root, textvariable=dcop_type_var, values=dcop_types)
    dcop_type_menu.grid(row=0, column=1, padx=10, pady=5)


def add_amount_agents_section(root):
    global agents_scale
    tk.Label(root, text="Amount of Agents (3-50):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    agents_scale.grid(row=1, column=1, padx=10, pady=5)


def add_seed_number_section(root):
    global seed_entry
    tk.Label(root, text="Seed Number:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    seed_entry.grid(row=2, column=1, padx=10, pady=5)


def add_algorithm_section(root):
    global algorithm_var
    tk.Label(root, text="Algorithm:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    algorithm_menu = ttk.Combobox(root, textvariable=algorithm_var, values=algorithms)
    algorithm_menu.grid(row=3, column=1, padx=10, pady=5)


def add_submit_button(root):
    tk.Button(root, text="Submit", command=lambda: submit(root)).grid(row=4, columnspan=2, pady=20)


def submit(root):
    global user_dcop_type, user_amount_agents, user_seed_number, user_algorithm

    user_dcop_type = dcop_type_var.get()
    user_amount_agents = agents_scale.get()
    user_seed_number = seed_entry.get()
    user_algorithm = algorithm_var.get()

    if not validate_seed_number(user_seed_number):
        return

    show_collected_information()

    root.destroy()
    open_hello_world_window()


def validate_seed_number(seed_number):
    try:
        int(seed_number)
        return True
    except ValueError:
        messagebox.showerror("Input Error", "Seed number must be an integer")
        return False


def show_collected_information():
    result = (f"DCOP Type: {user_dcop_type}\n"
              f"Amount of Agents: {user_amount_agents}\n"
              f"Seed Number: {user_seed_number}\n"
              f"Algorithm: {user_algorithm}")
    messagebox.showinfo("Submitted Information", result)


def open_hello_world_window():
    new_window = tk.Tk()
    new_window.title("Hello World")
    tk.Label(new_window, text="Hello, World!").pack(padx=50, pady=50)
    new_window.mainloop()


# Create the main window and run the application
root = create_main_window()
root.mainloop()
print()