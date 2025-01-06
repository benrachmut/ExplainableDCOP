import pickle
import statistics

from matplotlib import pyplot as plt

from XDCOPS import Explanation
from enums import ExplanationType

def get_explanation_summary_data(x_dcops_list):
    raw_data = {}
    for x_dcop in x_dcops_list:
        dcop = x_dcop.dcop
        query = x_dcop.query
        explanation = Explanation(dcop, query, explanation_type)
        for k, v in explanation.data_entry.items():
            if k not in raw_data: raw_data[k] = []
            raw_data[k].append(v)
    avg_data = {}
    for k, v in raw_data.items():
        avg_data[k] = sum(v) / len(v)#{"average": sum(v) / len(v), "std": statistics.stdev(v)}
    return avg_data

def change_data_structure(data_input):
    ans = {}
    for measure_name in Explanation.measure_names():
        if measure_name not in ans:
            ans[measure_name] = {}
        for query_type,num_vars_k_dict in data_input.items():
            if query_type not in ans[measure_name]:
                ans[measure_name][query_type] = {}
            for num_vars,measure_name_dict in num_vars_k_dict.items():
                ans[measure_name][query_type][num_vars] = measure_name_dict[measure_name]
    return ans


def get_data_for_graph():
    ans = {}
    for q_type,x_dcops_list in x_dcops_dict.items():
        query_type = q_type[0].name
        num_variables = q_type[1]

        if query_type not in ans:
            ans[query_type] = {}
        ans[query_type][num_variables]=get_explanation_summary_data(x_dcops_list)
        print(q_type)

    return change_data_structure(ans)


if __name__ == '__main__':
    #pickle_name = "xdcops_A_10_Dense Uniform_p1_0.7.pkl"
    pickle_name = "xdcops_A_10_Meeting Scheduling_meetings_8_per_agent_2.pkl"
    #pickle_name = "xdcops_A_10_Sparse Uniform_p1_0.2.pkl"


    #pickle_name = "xdcops_A_15_Sparse Uniform_p1_0.2.pkl"
    #pickle_name = "xdcops_A_20_Graph Coloring_p1_0.1.pkl"
    #pickle_name = "xdcops_A_25_Graph Coloring_p1_0.1.pkl"


    with open("xdcops_pickles/"+pickle_name, "rb") as file:
        x_dcops_dict = pickle.load(file)

    explanation_type = ExplanationType.BroadcastCentral
    ans = get_data_for_graph()

    line_type_dict = {"educated":'--',"rnd":"solid"}
    for measure,query_type_dict in ans.items():
        y_label = measure
        for query_type, data_dict in query_type_dict.items():
            line_type = query_type
            x = data_dict.keys()
            y = data_dict.values()
            plt.plot(
                x, y, label=explanation_type.name +"+"+query_type,color="black", linestyle=line_type_dict[query_type], linewidth=2
            )

        plt.xlabel("Number of Variables in Query" )
        plt.ylabel(y_label)
        #plt.title("Validation ** " + data_type_ + " **")
        plt.legend(title="Explanation and Query Type")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(measure+".pdf", bbox_inches='tight')  # Save as PDF

        plt.clf()




    #plt.plot(
    #    all_iterations, server_, label=k + "_server", color=colors_dict[k], linestyle='--', linewidth=2
    #)


    print()