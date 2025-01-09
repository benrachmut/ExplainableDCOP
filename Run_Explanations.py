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
        for num_vars,measure_name_dict in data_input.items():
                ans[measure_name][num_vars] = measure_name_dict[measure_name]
    return ans


def get_data_for_graph():
    ans = {}
    for num_variables,x_dcops_list in x_dcops_dict.items():
        ans[num_variables] = get_explanation_summary_data(x_dcops_list)

        print(num_variables)

    return change_data_structure(ans)


if __name__ == '__main__':
    #pickle_name = "xdcops_A_10_Dense Uniform_p1_0.7.pkl"
    exp_name = "xdcops_Meeting Scheduling_meetings_10_users_35_per_agent_2_time_slots_8"
    #pickle_name = "xdcops_A_10_Sparse Uniform_p1_0.2.pkl"


    #pickle_name = "xdcops_A_15_Sparse Uniform_p1_0.2.pkl"
    #pickle_name = "xdcops_A_20_Graph Coloring_p1_0.1.pkl"
    #pickle_name = "xdcops_A_25_Graph Coloring_p1_0.1.pkl"


    with open("xdcops_pickles/"+exp_name+".pkl", "rb") as file:
        x_dcops_dict = pickle.load(file)

    explanation_type = ExplanationType.BroadcastDistributed
    ans = get_data_for_graph()

    #line_type_dict = {"educated":'--',"rnd":"solid"}
    for measure,data_dict in ans.items():
        y_label = measure
        #for query_type, data_dict in query_type_dict.items():
        #line_type = query_type
        x = data_dict.keys()
        y = data_dict.values()
        plt.plot(
            x, y, label=explanation_type.name,color="black", linestyle="solid", linewidth=2
        )

        plt.xlabel("Number of Variables in Query" )
        plt.ylabel(y_label)
        #plt.title("Validation ** " + data_type_ + " **")
        plt.legend(title="Explanation Algorithm")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(measure+"_"+exp_name+".pdf", bbox_inches='tight')  # Save as PDF

        plt.clf()




    #plt.plot(
    #    all_iterations, server_, label=k + "_server", color=colors_dict[k], linestyle='--', linewidth=2
    #)


    print()