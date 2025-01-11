import pickle

from B_xdcop_files.Queries import QueryGenerator
from B_xdcop_files.XDCOPS import XDCOP
from enums import QueryType


def create_x_standard_dcop(dcop, seed_query, num_variables, num_values,with_connectivity_constraint,query_type):
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint,query_type).get_query()
    query.query_type = query_type

    return XDCOP(dcop, query)

def get_dcops_for_different_configs():
    ans = {}
    for density, dict_1 in dcops.items():
        print("density",density)
        ans[density] = {}
        for agent_size, dict_2 in dict_1.items():
            print("agent_size",agent_size)
            ans[density][agent_size] = {}
            algos_list = list(dict_2.keys())
            algos_to_remove = []
            for algo in algos_list:
                if len(dict_2[algo]) == 0:
                    algos_to_remove.append(algo)
            algos_list = [item for item in algos_list if item not in algos_to_remove]
            id_dcops_and_solutions_for_diff_algo = {}


            for dcop_id in dict_2[algos_list[0]]:
                id_dcops_and_solutions_for_diff_algo[dcop_id] = {}
                for algo in algos_list:
                    dcop_for_algo = dict_2[algo][dcop_id]
                    id_dcops_and_solutions_for_diff_algo[dcop_id][algo] = dcop_for_algo
            ans[density][agent_size] = id_dcops_and_solutions_for_diff_algo

    return ans

def get_x_dcops_dict(dcops_for_different_configs):
    ans = {}
    for density, dict_1 in dcops_for_different_configs.items():
        ans[density] = {}
        for agents_amount, dict_2 in dict_1.items():
            ans[density][agents_amount] = {}
            for query_type in query_types_list:
                ans[density][agents_amount][query_type] = {}
                amount_of_variables_list = range(min_vars, min(max_vars, agents_amount))
                for amount_of_vars in amount_of_variables_list:
                    ans[density][agents_amount][query_type][amount_of_vars] = {}
                    for dcop_id, dcops_dict in dict_2.items():

                        query_generator = QueryGenerator(dcops_dict, amount_of_vars, query_type)
                        #                      query_type).get_query()

                        for algo,dcop in dcops_dict.items():
                            if algo not in ans[density][agents_amount][query_type][amount_of_vars]:
                                ans[density][agents_amount][query_type][amount_of_vars][algo] = {}
                            query = query_generator.get_query(algo, dcop_id)
                            ans[density][agents_amount][query_type][amount_of_vars][dcop_id] = XDCOP(dcop,query)


def create_xdcop():

    dcops_for_different_configs = get_dcops_for_different_configs()
    return get_x_dcops_dict(dcops_for_different_configs)





        #for num_variables in nums_variables:
        #    ans[num_variables] = []

        #        for query_type in query_types:
        #            print("dcop id:",dcop.dcop_id,num_variables)
        #            dcop.create_agent_dict()

        #            for seed_ in seeds_xdcop:

        #                xdcop = create_x_standard_dcop(dcop, (seed_ + 1), num_variables, num_values,True,query_type)
        #                ans[num_variables].append(xdcop)

    #return ans


if __name__ == '__main__':
    folder_name ="B_xdcop_files/"
    file_name = "dcops_meeting_scheduling_v2"
    directory = folder_name+file_name

    with open(directory+".pkl", "rb") as file:
        dcops = pickle.load(file)
    seeds_xdcop = [1]
    min_vars = 2
    max_vars = 10
    query_types_list = [QueryType.rnd]#[QueryType.educated,QueryType.rnd]
    xdcops = create_xdcop()


    with open("xdcops_ " +file_name + ".pkl", "wb") as file:
        pickle.dump(xdcops, file)


