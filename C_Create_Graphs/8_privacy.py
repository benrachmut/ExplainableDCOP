import pickle
import matplotlib.pyplot as plt

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


from collections import defaultdict


def transform_data(input_dict):
    output_dict = {}

    for density, agent_data in input_dict.items():
        transformed = defaultdict(lambda: defaultdict(dict))

        for num_agents, comm_data in agent_data.items():
            for comm_type, measures in comm_data.items():
                for measure_name, value in measures.items():
                    transformed[measure_name][comm_type][num_agents] = value

        output_dict[density] = {k: dict(v) for k, v in transformed.items()}

    return output_dict

def plot_communication_curves(data,x_label,y_label):
    plt.figure(figsize=(10, 6))

    for comm_type, xy_values in data.items():
        x_values = list(xy_values.keys())
        y_values = list(xy_values.values())
        plt.plot(x_values, y_values, marker='o', label=comm_type)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.savefig(f"{folder_to_save}/{figure_name}.pdf", format="pdf", bbox_inches='tight')

    #plt.grid(True)
    #plt.show()



if __name__ == '__main__':
    scale = "dcop" #
    probs =["meeting_scheduling"] #["meeting_scheduling","random"]
    for is_with_legend in [True]:
        for is_with_normalized in [False]:
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
                avg_dict = transform_data(avg_dict)

                selected_vars_nums_list = range(1, 11)
                selected_explanation_types = list(ExplanationType)
                for measure in measure_names:
                    if prob == "meeting_scheduling":
                        y_name = measure
                        x_name = "Amount of Agents"
                        selected_density = 0.5
                        data =avg_dict[selected_density][measure]
                        folder_to_save, figure_name = get_folder_to_save_figure_name(graph_type+"_"+measure, prob, selected_density)
                        plot_communication_curves(data,x_name,y_name)


