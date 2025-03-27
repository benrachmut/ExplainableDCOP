import pickle

import numpy as np
from matplotlib import pyplot as plt

from C_Create_Graphs.Graph_functions import *
from enums import ExplanationType, QueryType
from matplotlib.lines import Line2D


def get_full_dict(densities,agent_amounts,query_type,algo,explanation_type,var_num):
    ans = {}
    for density in densities:
        ans[density] = {}

        for agent_amount in agent_amounts:
            ans[density][agent_amount] = {}

            input_dict = exp_dict[density][agent_amount][query_type][algo][var_num][explanation_type]
            ans[density][agent_amount] = input_dict


    return ans






def get_all_avg_dict():
    if prob == "meeting_scheduling":
        densities = [0.5]
    else:
        densities = [0.2,0.7]
    agent_amounts = [10,15,20,25,30,35,40,45,50]
    query_type = QueryType.rnd.name
    algo = "One_Opt"
    vars_num = 10
    explanation_type = "Shortest_Explanation"
    full_dict = get_full_dict(densities,agent_amounts,query_type,algo,explanation_type,vars_num)
    measure_dict = get_measure_dict(full_dict)
    return get_avg_dict(measure_dict)

def get_avg_dict(measure_dict):
    ans = {}
    for density, dict_1 in measure_dict.items():
        ans[density] = {}
        for amount_agents, dict_2 in dict_1.items():
            ans[density][amount_agents] = {}
            for comm_type, dict_3 in dict_2.items():
                ans[density][amount_agents][comm_type] = {}
                for measure,data_to_avg in dict_3.items():
                    ans[density][amount_agents][comm_type][measure] = sum(data_to_avg)/len(data_to_avg)
    return ans

def get_measure_dict(full_dict):
    ans = {}
    for density, dict_1 in full_dict.items():
        ans[density] = {}
        for amount_agents, dict_2 in dict_1.items():
            ans[density][amount_agents] = {}
            for comm_type, dict_3 in dict_2.items():
                ans[density][amount_agents][comm_type] = {}
                for measure in measure_names:
                    ans[density][amount_agents][comm_type][measure]=[]
                    for measure_single_dict in dict_3:
                        the_number = measure_single_dict[measure]
                        ans[density][amount_agents][comm_type][measure].append(the_number)
    return ans

def simply_avg_dict():
    ans = {}

    for query_name,query_new_name in selected_query_types_and_new_name.items():
        ans[query_new_name] = {}

        for exp_name,exp_new_name in selected_explanations_and_new_name.items():
            ans[query_new_name][exp_new_name] =  {}

            for var_num in selected_vars_nums_list:
                ans[query_new_name][exp_new_name][var_num]=  {}

                data_to_put = avg_dict[selected_density][query_name]["Complete"][var_num][exp_name]["BFS"]
                ans[query_new_name][exp_new_name][var_num]  = data_to_put
    return ans




if __name__ == '__main__':
    scale = "dcop" #
    probs =["random"] #["meeting_scheduling","random"]
    is_with_normalized=True
    for is_with_legend in [True,False]:
        for prob in probs:
            graph_type = "8_privacy"

            file_name = "explanations_"+scale+"_scale_"+prob+"_privacy.pkl"
            with open(file_name, "rb") as file:
                exp_dict = pickle.load(file)
            if is_with_normalized:
                measure_names =  [ "agent_privacy_normalized","topology_privacy_normalized","constraint_privacy_normalized","decision_privacy_with_send_sol_normalized","decision_privacy_without_send_sol_constraint_normalized"]

            else:
                measure_names =  [ "agent_privacy","topology_privacy","constraint_privacy","decision_privacy_with_send_sol_constraint","decision_privacy_without_send_sol_constraint"]
            avg_dict = get_all_avg_dict()


            selected_vars_nums_list = range(1, 11)
            selected_explanation_types = list(ExplanationType)


            curve_explanation_algos = {
                "CEDAR": 3,
                "CEDAR(O1)": 5,
                "CEDAR(O2)": 2,
                "CEDAR(V1)": 3,
                "CEDAR(V2)": 3
            }
            y_name = "Number of Constraints"
            x_name =  r" $|var(\sigma_Q)|$"

            selected_density = 0.2
            data = simply_avg_dict()
            folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)

            create_single_graph(is_with_legend,data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name, folder_to_save,
                                figure_name,
                                x_min = 1,x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,x_ticks=range(1,11))

            selected_density = 0.2
            data = simply_avg_dict()
            folder_to_save,figure_name = get_folder_to_save_figure_name(graph_type,prob,selected_density)

            create_single_graph(is_with_legend,data, ColorsInGraph.explanation_algorithms, curve_explanation_algos, x_name, y_name, folder_to_save,
                                figure_name,
                                x_min = 1,x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,x_ticks=range(1,11))

            if prob == "meeting_scheduling":
                selected_density = 0.5
                data = simply_avg_dict()
                folder_to_save, figure_name = get_folder_to_save_figure_name(graph_type, prob, selected_density)

                create_single_graph(is_with_legend, data, ColorsInGraph.explanation_algorithms, curve_explanation_algos,
                                    x_name, y_name, folder_to_save,
                                    figure_name,
                                    x_min=1, x_max=10, y_min=None, y_max=None, is_highlight_horizontal=False,
                                    x_ticks=range(1, 11))
