import tkinter as tk
from tkinter import ttk, messagebox

# Example choices for DCOP type and Algorithm
from enums import DcopType, Algorithm
from problems import DCOP_RandomUniform, DCOP_GraphColoring, DCOP

dcop_types = ["Graph Coloring", "Type2", "Type3"]
algorithms = ["Branch and Bound", "Algorithm2", "Algorithm3"]
dcop_type = None
algorithm = None
A = None
D = None
seed = None

# Global variables to store user's input
dcop_type_var = None
algorithm_var = None
agents_scale = None
domain_scale = None
seed_entry = None

user_dcop_type = None
user_amount_agents = None
user_domain = None
user_seed_number = None
user_algorithm = None


def initialize_shared_variables(root):
    global dcop_type_var, algorithm_var, agents_scale, seed_entry, domain_scale
    dcop_type_var = tk.StringVar(value=dcop_types[0])
    algorithm_var = tk.StringVar(value=algorithms[0])
    agents_scale = tk.Scale(root, from_=2, to=50, orient=tk.HORIZONTAL)
    agents_scale.set(10)
    domain_scale = tk.Scale(root, from_=2, to=50, orient=tk.HORIZONTAL)
    domain_scale.set(3)
    seed_entry = tk.Entry(root)
    seed_entry.insert(0, "0")  # Set default value to 0


def create_main_window():
    root = tk.Tk()
    root.title("DCOP Configuration")

    initialize_shared_variables(root)
    add_dcop_type_section(root)
    add_amount_agents_section(root)
    add_amount_domain_section(root)
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
    tk.Label(root, text="Amount of Agents (2-50):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    agents_scale.grid(row=1, column=1, padx=10, pady=5)


def add_amount_domain_section(root):
    global domain_scale
    tk.Label(root, text="Domain Size (2-50):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    domain_scale.grid(row=2, column=1, padx=10, pady=5)


def add_seed_number_section(root):
    global seed_entry
    tk.Label(root, text="Seed Number:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
    seed_entry.grid(row=3, column=1, padx=10, pady=5)


def add_algorithm_section(root):
    global algorithm_var
    tk.Label(root, text="Algorithm:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
    algorithm_menu = ttk.Combobox(root, textvariable=algorithm_var, values=algorithms)
    algorithm_menu.grid(row=4, column=1, padx=10, pady=5)


def add_submit_button(root):
    tk.Button(root, text="Submit", command=lambda: submit(root)).grid(row=5, columnspan=2, pady=20)


def submit(root):
    global user_dcop_type, user_amount_agents, user_domain, user_seed_number, user_algorithm

    user_dcop_type = dcop_type_var.get()
    user_amount_agents = agents_scale.get()
    user_domain = domain_scale.get()
    user_seed_number = seed_entry.get()
    user_algorithm = algorithm_var.get()

    if not validate_seed_number(user_seed_number):
        return

    #show_collected_information()

    root.destroy()

def validate_seed_number(seed_number):
    try:
        seed_int = int(seed_number)
        if seed_int >= 0:
            return True
        else:
            messagebox.showerror("Input Error", "Seed number must be a positive integer")
            return False
    except ValueError:
        messagebox.showerror("Input Error", "Seed number must be an integer")
        return False


def show_collected_information():
    result = (f"DCOP Type: {user_dcop_type}\n"
              f"Amount of Agents: {user_amount_agents}\n"
              f"Domain Size: {user_domain}\n"
              f"Seed Number: {user_seed_number}\n"
              f"Algorithm: {user_algorithm}")
    messagebox.showinfo("Submitted Information", result)


def open_hello_world_window():
    new_window = tk.Tk()
    new_window.title("Hello World")
    tk.Label(new_window, text="Hello, World!").pack(padx=50, pady=50)
    new_window.mainloop()


def init_dcop_type():
    if user_dcop_type == "Graph Coloring":
        global dcop_type
        dcop_type = DcopType.graph_coloring



def init_algorithm_type():
    if user_algorithm == "Branch and Bound":
        global algorithm
        algorithm = Algorithm.branch_and_bound
        print()


def init_globals():
    init_dcop_type()
    init_algorithm_type()
    global A,D,seed
    A = user_amount_agents
    D = user_domain
    seed = int(user_seed_number)


# Create the main window and run the application
def create_dcop():
    if dcop_type == DcopType.sparse_random_uniform:
        dcop_name = "Sparse Uniform"
        return DCOP_RandomUniform(seed, A, D, dcop_name, algorithm)
    if dcop_type == DcopType.graph_coloring:
        dcop_name = "Graph Coloring"
        return DCOP_GraphColoring(seed, A, D, dcop_name, algorithm)

def open_agent_input_window(dcop):
    agent_window = tk.Tk()
    agent_window.title("Agent Input")

    tk.Label(agent_window, text="Which Agent are you?").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    agent_number = tk.Scale(agent_window, from_=1, to=user_amount_agents, orient=tk.HORIZONTAL)
    agent_number.grid(row=0, column=1, padx=10, pady=5)

    result_label = tk.Label(agent_window, text="")
    result_label.grid(row=2, columnspan=2, pady=20)

    tk.Button(agent_window, text="See Results", command=lambda: show_agent_results(agent_number.get(), result_label,dcop)).grid(row=1, columnspan=2, pady=20)

    agent_window.mainloop()


def get_selected_agent_obj(agent_number, dcop:DCOP):
    for a in dcop.agents:
        if a.id_ == agent_number:
            return a


def show_agent_results(agent_number, result_label,dcop:DCOP):
    agent = get_selected_agent_obj(agent_number, dcop)
    result = "Results for A_"+str(agent_number)+"="+str(agent.anytime_variable)
    result_label.config(text=result)

    # Example dictionary for demonstration purposes
    result_dict = {1: 10, 2: 20, 3: 30}

    # Create checkboxes for the result dictionary
    checkboxes = create_checkboxes(result_label.master, result_dict)

    # Add a button to process the selected checkboxes
    tk.Button(result_label.master, text="Submit Selections",
              command=lambda: process_selections(checkboxes, result_dict)).grid(row=4 + len(result_dict), columnspan=2,
                                                                                pady=20)


def create_checkboxes(parent, result_dict):
    tk.Label(parent, text="Get an explanation for your value, given the selection of which neighbors:").grid(row=3,
                                                                                                             columnspan=2,
                                                                                                             pady=10)

    checkboxes = {}
    for idx, (key, value) in enumerate(result_dict.items()):
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(parent, text=f"A_{key}:{value}", variable=var)
        checkbox.grid(row=4 + idx, columnspan=2, sticky='w', padx=20)
        checkboxes[key] = var
    return checkboxes


def process_selections(checkboxes, result_dict):
    selected_checkboxes = {key: result_dict[key] for key, var in checkboxes.items() if var.get()}
    print(f"Selected Checkboxes: {selected_checkboxes}")  # Replace with actual processing logic


if __name__ == '__main__':

    root = create_main_window()
    root.mainloop()
    init_globals()
    dcop = create_dcop()
    dcop.execute()
    open_agent_input_window(dcop)
    show_agent_results()


    print()




    open_hello_world_window()
