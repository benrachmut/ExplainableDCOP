import pickle

from enums import QueryType


def create_xdcop(dcops,nums_variable,num_values = 1):
    ans = {}

    for num_variables in nums_variables:
        ans[num_variables] = []

        for dcop in dcops:
            print("dcop id:",dcop.dcop_id,num_variables)
            dcop.create_agent_dict()
            for seed_ in seeds_xdcop:
                if dcop_type == DcopType.meeting_scheduling:
                    xdcop = create_x_MeetingSchedualing_dcop(dcop, seed_ + 1, num_variables, num_values,
                                                             with_connectivity_constraint, query_type)
                else:
                    xdcop = create_x_standard_dcop(dcop, (seed_ + 1), num_variables, num_values,with_connectivity_constraint,query_type)
                ans[num_variables].append(xdcop)

    return ans


if __name__ == '__main__':

    algos = ["mgm","bnb"]
    dcops = []
    with open("xdcops_pickles/"+exp_name+".pkl", "rb") as file:
        x_dcops_dict = pickle.load(file)
    seeds_xdcop = [1]
    max_vars = 10
    nums_variables = ans = range(1, max_vars + 1)
    query_types = [QueryType.educated,QueryType.rnd]


    xdcops = create_xdcop(nums_variables ,)


    with open("xdcops_ " +dcops[0].create_summary() + ".pkl", "wb") as file:
        pickle.dump(xdcops, file)


