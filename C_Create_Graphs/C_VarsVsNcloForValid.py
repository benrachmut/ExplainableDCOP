import pickle

import numpy as np

from enums import ExplanationType, QueryType

with open("explanations.pkl", "rb") as file:
    exp_dict = pickle.load(file)

density = 0.7
agent_amount = 10
query_type = QueryType.rnd.name
explanation_type = [ExplanationType.CEDAR_opt2.name, ExplanationType.CEDAR_opt3A.name]
measure_name =  "Alternative # Constraint"#"NCLO_for_valid_solution" #"Delta Cost per Constraint" "Alternative # Constraint", "NCLO_for_valid_solution"

dict_1 = exp_dict[density][agent_amount][query_type]
x_y_full_dict = {}
for algo, dict_2 in dict_1.items():
    x_y_full_dict[algo] = {}
    for vars_num,dict_3 in dict_2.items():
        x_y_full_dict[algo][vars_num] = {}
        for exp_type, explanations in dict_3.items():
            x_y_full_dict[algo][vars_num][exp_type] = []
            for explanation in explanations:
                x_y_full_dict[algo][vars_num][exp_type].append(explanation.data_entry[measure_name])


x_y_avg_dict={}
for algo, dict_1 in x_y_full_dict.items():
    x_y_avg_dict[algo] = {}
    for vars_num, dict_2 in dict_1.items():
        x_y_avg_dict[algo][vars_num] = {}
        for exp_type, measure_ in dict_2.items():
            x_y_avg_dict[algo][vars_num][exp_type] = np.mean(measure_)

print()



