import pickle

import numpy as np

from enums import ExplanationType, QueryType

with open("explanations_query_scale_meeting_scheduling.pkl", "rb") as file:
    exp_dict = pickle.load(file)

density = 0.7
agent_amount = 10
query_types = list(QueryType)#QueryType.rnd.name
explanation_type = [ExplanationType.CEDAR_opt2.name, ExplanationType.CEDAR_opt3A.name]
num_vars = 10
measure_name =  "Alternative_delta_cost_per_addition"#"NCLO_for_valid_solution" #"Delta Cost per Constraint" "Alternative # Constraint", "NCLO_for_valid_solution"

dict_1 = exp_dict[density][agent_amount]

max_size = 0
x_y_full_dict = {}

for query_name, dict_2 in dict_1.items():
    x_y_full_dict[query_name] = {}
    for algo, dict_3 in dict_2.items():
        x_y_full_dict[query_name][algo] = {}
        for exp_type,explanations in dict_3[num_vars].items():
            x_y_full_dict[query_name][algo][exp_type] = []
            for explanation in explanations:
                data_ = explanation[measure_name]
                if len(data_) > max_size:
                    max_size = len(data_)
                x_y_full_dict[query_name][algo][exp_type].append(data_)


#x_y_full_V2_dict = {}
#for algo,dict_1 in x_y_full_dict.items():
#    x_y_full_V2_dict[algo] = {}
#    for

x_y_full_V2_dict={}
for query_name, dict_1 in x_y_full_dict.items():
    x_y_full_V2_dict[query_name] = {}
    for algo, dict_2 in dict_1.items():
        x_y_full_V2_dict[query_name][algo] = {}
        for exp_type, all_lists_of_values in dict_2.items():
            x_y_full_V2_dict[query_name][algo][exp_type] = {}

            counter = 0
            for list_of_values in all_lists_of_values:
                max_val = max(list_of_values)
                while len(list_of_values)<max_size:
                    list_of_values.append(max_val)
                x_y_full_V2_dict[query_name][algo][exp_type][counter] = list_of_values
                counter = counter + 1


all_vals_per_constraint = {}
for query_name, dict_1 in x_y_full_V2_dict.items():
    all_vals_per_constraint[query_name] = {}
    for algo, dict_2 in dict_1.items():
        all_vals_per_constraint[query_name][algo] = {}
        for exp_type, all_lists_of_values in dict_2.items():
            all_vals_per_constraint[query_name][algo][exp_type] = {}
            all_explanations_dict = x_y_full_V2_dict[query_name][algo][exp_type]
            for iteration in range(max_size):
                iter_list = []
                for explanation_index in all_explanations_dict.keys():
                    iter_list.append(all_explanations_dict[explanation_index][iteration])
                all_vals_per_constraint[query_name][algo][exp_type][iteration] = sum(iter_list)/len(iter_list)


print()







