import pickle

import numpy as np
from matplotlib import pyplot as plt
from pulp import initialize

from C_Create_Graphs.Graph_functions import *
from enums import ExplanationType, QueryType
from matplotlib.lines import Line2D


def get_full_dict(densities,agent_amount,query_types,algos,vars_nums_list,explanation_types):
    ans = {}
    for density in densities:
        ans[density] = {}
        for query_type in query_types:
            ans[density][query_type] = {}
            for algo in algos:
                ans[density][query_type][algo] = {}
                for var_num in vars_nums_list:
                    ans[density][query_type][algo][var_num] = {}
                    for explanation_type in explanation_types:
                        input_dict = exp_dict[density][agent_amount][query_type][algo][var_num][explanation_type]
                        ans[density][query_type][algo][var_num][explanation_type] = input_dict

    return ans


def get_measure_dict(full_dict):
    ans = {}
    for density, dict_1 in full_dict.items():
        ans[density] = {}
        for query_type, dict_2 in dict_1.items():
            ans[density][query_type] = {}
            for algo,dict_3 in dict_2.items():
                ans[density][query_type][algo] = {}
                for var_num, dict_4 in dict_3.items():
                    ans[density][query_type][algo][var_num] = {}
                    for explanation_type,measures_all_dicts in dict_4.items():
                        ans[density][query_type][algo][var_num][explanation_type] = []
                        for measure_single_dict in measures_all_dicts:
                            measure_to_add = measure_single_dict[measure_name]
                            ans[density][query_type][algo][var_num][explanation_type].append(measure_to_add)
    return ans

def get_list_per_iteration(measures_lists,i):
    ans = []
    for single_list in measures_lists:
        if i<len(single_list) :
            ans.append( single_list[i])
        else:
            ans.append( single_list[len(single_list)-1])
    return ans


def done_all_iterations(measures_lists,i):
    for single_list in measures_lists:
        if i<len(single_list):
            return False
    return True

def get_avg_dict(measure_dict):
    ans = {}
    for density, dict_1 in measure_dict.items():
        ans[density] = {}
        for query_type, dict_2 in dict_1.items():
            ans[density][query_type] = {}
            for algo, dict_3 in dict_2.items():
                ans[density][query_type][algo] = {}
                for var_num, dict_4 in dict_3.items():
                    ans[density][query_type][algo][var_num] = {}
                    for explanation_type, measures_lists in dict_4.items():
                        i = 0
                        avg_per_iter = {}
                        while not done_all_iterations(measures_lists,i) :
                            list_of_iteration = get_list_per_iteration(measures_lists,i)
                            avg_per_iter[i] = sum(list_of_iteration)/len(list_of_iteration)
                            i = i+1

                        ans[density][query_type][algo][var_num][explanation_type] = avg_per_iter


                        #for delta_per_nclo_list in measures_list:

                        #avg_ = sum(measures_list) / len(measures_list)
                        #ans[density][query_type][algo][var_num][explanation_type] = avg_

    return ans


def get_all_avg_dict():
    densities = [0.2,  0.7]
    agent_amount = 10
    query_types = [QueryType.educated.name, QueryType.rnd.name]
    algos = ["Complete", "One_Opt"]
    vars_nums_list = range(1, 11)
    explanation_types = []
    for exp_type in list(ExplanationType): explanation_types.append(exp_type.name)

    full_dict = get_full_dict(densities,agent_amount,query_types,algos,vars_nums_list,explanation_types)
    measure_dict = get_measure_dict(full_dict)
    return get_avg_dict(measure_dict)



def simply_avg_dict():
    initial_ans = {}
    max_size = 0
    for query_name,query_new_name in selected_query_types_and_new_name.items():
        initial_ans[query_new_name] = {}

        for exp_name,exp_new_name in selected_explanations_and_new_name.items():
            initial_ans[query_new_name][exp_new_name] =  {}

            initial_ans[query_new_name][exp_new_name]=  {}

            data_to_put = avg_dict[selected_density][query_name]["Complete"][selected_vars_num][exp_name]
            initial_ans[query_new_name][exp_new_name] = data_to_put
            if len(data_to_put)>max_size:
                max_size = len(data_to_put)
    ans = {}
    for query, dict_1 in initial_ans.items():
        ans[query] = {}
        for exp_name, dict_2 in dict_1.items():
            dict_size = len(dict_2)
            if dict_size<max_size:
                what_to_add = dict_2[dict_size-1]
                for k in range(dict_size+1,max_size+1):
                    dict_2[k] = what_to_add

            ans[query][exp_name] = dict_2


    return ans



if __name__ == '__main__':
    scale = "query" #
    prob ="meeting_scheduling" #"meeting_scheduling" #"random"
    folder_to_save = "4_constraint_count_delta_cost_exp"


    graph_type = "4_constraint_count_delta_cost_exp"
    file_name = "explanations_"+scale+"_scale_"+prob+".pkl"
    with open(file_name, "rb") as file:
        exp_dict = pickle.load(file)
    measure_name =  "Alternative_delta_cost_per_addition"#NCLO_for_valid_solution" #"Cost delta of All Alternatives""Cost delta of Valid"
    avg_dict = get_all_avg_dict()


    selected_vars_num = 10
    selected_explanation_types = list(ExplanationType)

    axes_titles_font = 14
    axes_number_font = 14





    if prob == "meeting_scheduling":  # random:
        y_name = r"$\Delta$ cost (Symlog Scale)"
    else:
        y_name = r"$\Delta$ cost"
    x_name = "NCLO"

    curve_explanation_algos = {
        "Grounded_Constraints(O1)": 3,
        "Shortest_Explanation(O2)": 3,
        "Sort_Parallel(O3)": 3,
        "Sort_Parallel(O3)*": 3,
        # "Varint(Mean)":"brown",
        "Varint(Max)": 3
    }
    if prob=="meeting_scheduling":
        manipulate_y=True
    else:
        manipulate_y=False

    selected_density = 0.7
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph(data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name,
                        folder_to_save,
                        figure_name,manipulate_y=manipulate_y,
                        x_min=None, x_max=None, y_min=None, y_max=None, is_highlight_horizontal=False, x_ticks=None, with_points = False)


    selected_density = 0.2
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph(data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name,
                        folder_to_save,
                        figure_name, manipulate_y=manipulate_y,
                        x_min=None, x_max=None, y_min=None, y_max=None, is_highlight_horizontal=False, x_ticks=None,with_points = False)



