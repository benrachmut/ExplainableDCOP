import pickle

import numpy as np

from enums import ExplanationType, QueryType

with open("explanations.pkl", "rb") as file:
    exp_dict = pickle.load(file)

density = 0.7
agent_amount = 10
query_type = QueryType.educated.name
explanation_type = ExplanationType.CEDAR_opt2.name
measure_name =  "Cost delta of Valid" #"Cost delta of All Alternatives""Cost delta of Valid"

dict_1 = exp_dict[density][agent_amount][query_type]
x_y_full_dict = {}
for algo, dict_2 in dict_1.items():
    x_y_full_dict[algo] = {}
    for vars_num,dict_3 in dict_2.items():
        x_y_full_dict[algo][vars_num] = []
        for exp_type, explanations in dict_3.items():
            for explanation in explanations:
                x_y_full_dict[algo][vars_num].append(explanation.data_entry[measure_name])


x_y_avg_dict={}
for algo, dict_1 in x_y_full_dict.items():
    x_y_avg_dict[algo] = {}
    for vars_num, vals_to_avg in dict_1.items():
        x_y_avg_dict[algo][vars_num] = np.mean(vals_to_avg)

print()



