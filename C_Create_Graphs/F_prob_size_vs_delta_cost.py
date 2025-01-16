import pickle

import numpy as np
from matplotlib import pyplot as plt

from enums import ExplanationType, QueryType
from matplotlib.lines import Line2D


def get_full_dict(densities,agents_amounts,query_types,algos,explanation_type,vars_nums_list):
    ans = {}

    for density in densities:
        ans[density] = {}
        for query_type in query_types:
            ans[density][query_type] = {}
            for algo in algos:

                ans[density][query_type][algo] = {}
                for var_num in vars_nums_list:
                    ans[density][query_type][algo][var_num] = {}
                    for agent_amount in agents_amounts:
                        if algo == "bnb" and agent_amount>10:
                            break
                        input_dict = exp_dict[density][agent_amount][query_type][algo][var_num][explanation_type]
                        ans[density][query_type][algo][var_num][agent_amount]= input_dict

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
                            ans[density][query_type][algo][var_num][explanation_type].append(measure_single_dict[measure_name])
    return ans


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
                    for explanation_type, measures_list in dict_4.items():
                        avg_ = sum(measures_list) / len(measures_list)
                        ans[density][query_type][algo][var_num][explanation_type] = avg_

    return ans


def get_all_avg_dict():
    densities = [0.2, 0.5, 0.7]
    agents_amounts = range(5, 55,5)
    query_types = [QueryType.educated.name, QueryType.semi_educated.name, QueryType.rnd.name]
    algos = ["bnb", "mgm"]
    vars_nums_list = [1,5]
    explanations_type = ExplanationType.CEDAR_opt2.name

    full_dict = get_full_dict(densities,agents_amounts,query_types,algos,explanations_type,vars_nums_list)
    measure_dict = get_measure_dict(full_dict)
    return get_avg_dict(measure_dict)


def simply_avg_dict():
    ans = {}

    for query_name,query_new_name in selected_query_types_and_new_name.items():
        ans[query_new_name] = {}
        for algo,algo_new_name in selected_algos_and_new_name.items():
            ans[query_new_name][algo_new_name] = {}
            for agent_amount in range(5,55,5):
                ans[query_new_name][algo_new_name] =avg_dict[selected_density][query_name][algo][selected_var]

    return ans


def create_single_graph():
    plt.figure(figsize=(12, 6))

    for primary_key, sub_dict in data.items():
        for sub_key, values in sub_dict.items():
            x = list(values.keys())  # X-axis values (range(1,11))
            y = list(values.values())  # Apply log if positive, otherwise handle negatives
            if prob == "meeting_scheduling":  # random:
                plt.yscale('symlog', linthresh=1)
        plt.plot(x, y, linewidth=linewidth, linestyle=line_styles[primary_key], color=colors[sub_key],
                     label=f"{sub_key} ({primary_key})")

    # Add labels, title, and legends
    plt.xlabel(x_name, fontsize=axes_titles_font)  # Increase font size for x-axis label
    plt.ylabel(y_name, fontsize=axes_titles_font)

    # Custom legends
    color_legend = [Line2D([0], [0], color=colors[key], lw=2, label=key) for key in colors]
    line_legend = [Line2D([0], [0], color='black', linestyle=line_styles[key], lw=2, label=key) for key in line_styles]

    # Place line type legend at the side of the graph (top)
    first_legend = plt.legend(handles=line_legend, title="Query Type", loc="center left", bbox_to_anchor=(1.05, 0.5),
                              borderaxespad=0., frameon=False, handlelength=2.5, fontsize=10)
    plt.gca().add_artist(first_legend)

    # Place algorithm color legend below the first legend
    plt.legend(handles=color_legend, title="Algorithm", loc="center left", bbox_to_anchor=(1.05, 0.2), borderaxespad=0.,
               frameon=False, handlelength=2.5, fontsize=10)

    # Highlight y = 0 line
    plt.xlim(left=10)

    plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='y = 0')

    plt.grid(True)

    # Increase font size of the axis tick labels
    plt.tick_params(axis='both', which='major', labelsize=14)  # Increase size of tick labels

    # Show the plot
    plt.tight_layout(pad=5.0)  # Increase padding for better spacing
    plt.savefig(folder_to_save+"/"+figure_name + ".pdf", format="pdf")
    plt.savefig(folder_to_save+"/"+figure_name + ".jpeg", format="jpeg")
    # plt.show()
    plt.clf()

if __name__ == '__main__':
    is_clear = False

    scale = "dcop" #
    prob ="meeting_scheduling" #"meeting_scheduling" #"random"
    if is_clear:
        folder_to_save = "F_prob_size_vs_delta_cost_clear"
    else:
        folder_to_save = "F_prob_size_vs_delta_cost"

    graph_type = "F_ProbSizeVsDeltaCost"
    file_name = "explanations_"+scale+"_scale_"+prob+".pkl"
    with open(file_name, "rb") as file:
        exp_dict = pickle.load(file)
    measure_name =  "Cost delta of Valid" #"Cost delta of All Alternatives""Cost delta of Valid"
    avg_dict = get_all_avg_dict()

    if is_clear:
        selected_query_types_and_new_name = {QueryType.educated.name: "Educated",QueryType.rnd.name: "Random"}
    else:
        selected_query_types_and_new_name = {QueryType.educated.name: "Educated",
                                             QueryType.semi_educated.name: "Educated*",
                                             QueryType.rnd.name: "Random"}




    axes_titles_font = 14
    axes_number_font = 14
    linewidth = 3

    if is_clear:
        selected_query_types_and_new_name = {QueryType.educated.name: "Educated", QueryType.rnd.name: "Random"}
    else:
        selected_query_types_and_new_name = {QueryType.educated.name: "Educated",
                                             QueryType.semi_educated.name: "Educated*",
                                             QueryType.rnd.name: "Random"}

    selected_algos_and_new_name = {"bnb": "Complete", "mgm": "1-Opt"}

    if is_clear:
        line_styles = {'Educated': '-', 'Random': '--', }
    else:
        line_styles = {'Educated': '-', 'Educated*': '-.', 'Random': '--', }
    colors = {'Complete': 'blue', '1-Opt': 'red'}

    if prob == "meeting_scheduling":  # random:
        y_name = r"$\Delta$ cost (Symlog Scale)"
    else:
        y_name = (r"$\Delta$ cost")
    selected_var = 5
    x_name = "Amount of Agents"
    selected_density = 0.7
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph()

    selected_density = 0.5
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph()

    selected_density = 0.2
    data = simply_avg_dict()
    figure_name = graph_type+"_"+prob+"_"+str(int(selected_density*10))
    create_single_graph()
