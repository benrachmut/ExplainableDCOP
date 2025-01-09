import pickle

from Queries import QueryGenerator
from XDCOPS import XDCOP
from enums import QueryType, DcopType

def create_x_standard_dcop(dcop, seed_query, num_variables, num_values,with_connectivity_constraint,query_type):
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint,query_type).get_query()
    query.query_type = query_type

    return XDCOP(dcop, query)

def create_xdcop(dcops,nums_variable,num_values = 1):
    ans = {}

    for num_variables in nums_variables:
        ans[num_variables] = []

        for dcop in dcops:
            for query_type in query_types:
                print("dcop id:",dcop.dcop_id,num_variables)
                dcop.create_agent_dict()
                for seed_ in seeds_xdcop:

                    xdcop = create_x_standard_dcop(dcop, (seed_ + 1), num_variables, num_values,True,query_type)
                    ans[num_variables].append(xdcop)

    return ans


if __name__ == '__main__':
    file_name = "dcops_meeting_scheduling_v2"

    with open(file_name+".pkl", "rb") as file:
        dcops = pickle.load(file)
    seeds_xdcop = [1]
    max_vars = 10
    nums_variables = ans = range(1, max_vars + 1)
    query_types = [QueryType.educated,QueryType.rnd]


    xdcops = create_xdcop(nums_variables ,)


    with open("xdcops_ " +dcops[0].create_summary() + ".pkl", "wb") as file:
        pickle.dump(xdcops, file)


