import pickle

if __name__ == '__main__':
    pickle_name = "xdcops_A_5_Dense Uniform_p1_0.7.pkl"
    #pickle_name = "xdcops_A_5_Dense Uniform_p1_0.7"

    with open(pickle_name, "rb") as file:
        x_dcops = pickle.load(file)
