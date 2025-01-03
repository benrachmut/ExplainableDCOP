import pickle

if __name__ == '__main__':
    #pickle_name = "xdcops_A_5_Dense Uniform_p1_0.7.pkl"
    #pickle_name = "xdcops_A_5_Sparse Uniform_p1_0.2.pkl"
    #pickle_name = "xdcops_A_5_Graph Coloring_p1_0.1.pkl"
    pickle_name ="xdcops_A_5_Meeting Scheduling_meetings_2_per_agent_2.pkl"
    with open(pickle_name, "rb") as file:
        x_dcops = pickle.load(file)
    print()