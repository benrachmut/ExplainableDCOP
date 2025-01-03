import pickle

import matplotlib.pyplot as plt

from Globals_ import *
from XDCOPS import *
from problems import *
from Functions import *



def get_name_of_exp(A,property="complete"):
    if dcop_type!=DcopType.meeting_scheduling:
        return str(dcop_type.name) + "_" + property + "_agents" + str(A)
    else:
        return str(dcop_type.name) + "_" + property + "_meetings_" + str(meetings)+"_per_agents_"+str(meetings_per_agent)


def get_pickle_name(A,property="complete"):
    return get_name_of_exp(A,property)+".pkl"

def get_DCOP(i,algorithm,dcop_type,A = 50):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i, A, sparse_D, "Sparse Uniform", algorithm,sparse_p1)
    if dcop_type == DcopType.dense_random_uniform:
        return DCOP_RandomUniform(i, A, dense_D, "Dense Uniform", algorithm,dense_p1)
    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, "Graph Coloring", algorithm)
    if dcop_type == DcopType.meeting_scheduling:
        return DCOP_MeetingSchedualing(id_=i, A=A, meetings=meetings, meetings_per_agent=meetings_per_agent,
                                        time_slots_D=time_slots_D, dcop_name="Meeting Schedualing",
                                       algorithm = algorithm)

def read_pickle_files(folder_name):
    """
    Reads all pickle files in the specified folder and returns a list of their contents.

    Args:
        folder_name (str): The name of the folder containing pickle files.

    Returns:
        list: A list of objects read from the pickle files.
    """
    # Get the absolute path of the folder
    folder_path = os.path.abspath(folder_name)

    # Check if the folder exists
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")

    contents = []

    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Only process files with .pkl or .pickle extension
        if file_name.endswith(('.pkl', '.pickle')):
            file_path = os.path.join(folder_path, file_name)

            # Open and load the pickle file
            with open(file_path, 'rb') as file:
                content = pickle.load(file)
                contents.append(content)

    return contents


def create_dcops():
    for A in amount_agents:
        dcops_complete = []
        for i in range(repetitions):
            print("start", dcop_type, "number:", i)

            dcop = get_DCOP(i, algorithm, dcop_type, A)
            # draw_dcop(dcop)
            if is_center_solver:
                dcop.execute_center()
            else:
                dcop.execute_distributed()
            dcops_complete.append(dcop)
            # Open a file to save the pickle
            pickle_name = get_pickle_name(A, "complete")
            with open(pickle_name, "wb") as file:
                pickle.dump(dcops_complete, file)


def get_dcops(A, property= "complete"):
    pickle_name = get_pickle_name(A, property)
    with open(pickle_name, "rb") as file:
        return pickle.load(file)


def create_x_standard_dcop(dcop, seed_query, num_variables, num_values,with_connectivity_constraint):
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint,query_type).get_query()
    query.query_type = query_type

    return XDCOP(dcop, query,explanation_type)

def create_x_MeetingSchedualing_dcop(dcop, seed_query, num_meeting, num_alternative_slot,with_connectivity_constraint):
    qg = QueryGeneratorScheduling(dcop, seed_query, num_meeting, num_alternative_slot, with_connectivity_constraint,query_type)
    query =qg.get_query()
    query.query_type = query_type
    return XDCOP(dcop, query,explanation_type)

def create_meeting_x_dcops():
    for num_meeting in num_meetings:
        for num_alternative_slot in num_alternative_slots:
            #data_prep = PrepData(num_variables, num_values)
            #print(data_prep)
            x_dcops = []
            for dcop in dcops:
                print(dcop.dcop_id)
                dcop.create_agent_dict()
                for seed_ in seeds_xdcop:
                    xdcop = create_x_MeetingSchedualing_dcop(dcop, seed_+1, num_meeting, num_alternative_slot,with_connectivity_constraint)
                    x_dcops.append(xdcop)
            return xdcop
def create_xdcop():
    for num_variables in nums_variables:
        for num_values in nums_values:
            #data_prep = PrepData(num_variables, num_values)
            #print(data_prep)
            x_dcops = []
            for dcop in dcops:
                print(dcop.dcop_id)
                dcop.create_agent_dict()
                for seed_ in seeds_xdcop:
                    xdcop = create_x_standard_dcop(dcop, (seed_ + 1), num_variables, num_values,with_connectivity_constraint)
                    x_dcops.append(xdcop)
            return xdcop

                    #query_generator = QueryGenerator(dcop, (seed_ + 1), num_variables, num_values,
                                                     #with_connectivity_constraint)
                    #query = query_generator.get_query()
                    #x_dcops.append(XDCOP(dcop, query,explanation_type))


            #data_prep.execute_data(x_dcops)

            #pickle_name = str(data_prep) + get_pickle_name(A, "complete")
            #with open(pickle_name, "wb") as file:
            #    pickle.dump(data_prep, file)


if __name__ == '__main__':
    run_what = RunWhat.dcops


    dcop_type = DcopType.dense_random_uniform
    repetitions = 100
    is_center_solver = True
    A = 20

    meetings = 15
    meetings_per_agent = 2
    time_slots_D = 10



    explanation_type = ExplanationType.BroadcastCentral
    query_type = QueryType.educated
    with_connectivity_constraint = True
    seeds_xdcop = [1]  # range(0, 2)
    nums_variables = [8]  # [1, 5, 9]  # range(2, A)
    nums_values = [1]  # [1,2,3,4,5]#[1,5,9]  # range(1, max_domain-1)

    num_meetings = [2,3]
    num_alternative_slots = [1]

    if run_what == RunWhat.dcops :
        create_dcops()
    if run_what == RunWhat.xdcops :
        dcops = get_dcops(A)
        # max_domain = len(dcops[0].agents[0].domain)
        if dcop_type == DcopType.meeting_scheduling:
            x_dcops = create_meeting_x_dcops()
        else:
            x_dcops = create_xdcop()

    #if run_what == RunWhat.handle_data:
    #    xdcops_data = read_pickle_files(get_name_of_exp(A,property="complete"))
    #    xdcop_by_var = {}
    #    for xdcop_data in xdcops_data:
    #        num_variables = xdcop_data.num_variables
    #        if num_variables not in xdcop_by_var:
    #            xdcop_by_var[num_variables] = []
    #        xdcop_by_var[num_variables].append(xdcop_data)

    #    colors = ["blue", "green", "red", "orange","purple"]

    #    for variables, datas_ in xdcop_by_var.items():
    #        labels = []
    #        dicts = []
    #        for data_ in datas_:
    #            dicts.append(data_.avg_cum_delta_over_dcop)
    #            labels.append(str(data_.num_values))
    #        plot_dictionaries(dicts, colors, labels,variables,"Amount of Values",get_name_of_exp(A))





