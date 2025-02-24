import pickle
import matplotlib.pyplot as plt


def extract_data():
    with open("test_k_opt.pkl", 'rb') as file:
        return pickle.load(file)


def gets_costs_per_iter():
    ans = {}
    for how_may_opt, dcop_dict in data_.items():
        ans_per_opt = {}
        for i in range(101):
            ans_per_opt[i] = []

        for dcop_id, dcop in dcop_dict.items():
            global_cost = dcop.kopt.global_cost
            for i, cost in global_cost.items():
                ans_per_opt[i].append(cost)
        ans[how_may_opt] = ans_per_opt
    return ans

def get_avg_k_opt():
    ans1 = {}
    for amount_opt, cost_dict in data_.items():
        ans1[amount_opt] = {}
        for i, cost_list in cost_dict.items():
            ans1[amount_opt] [i] = sum(cost_list) / len(cost_list)

    ans2 = {}
    for amount_opt, cost_dict1 in ans1.items():
        if amount_opt == "One_Opt":
            ans2["1_opt"] =cost_dict1
        if amount_opt == "Two_Opt":
            ans2["2_opt"]=cost_dict1
        if amount_opt == "Three_Opt":
            ans2["3_opt"]=cost_dict1
        if amount_opt == "Four_Opt":
            ans2["4_opt"]=cost_dict1
        if amount_opt == "Five_Opt":
            ans2["5_opt"]=cost_dict1
    sorted_dict = dict(sorted(ans2.items()))

    return sorted_dict
if __name__ == '__main__':
    data_ = extract_data()
    data_ = data_[0.2][50]
    data_ = gets_costs_per_iter()
    data_ = get_avg_k_opt()

    plt.figure(figsize=(8, 6))

    for opt, values in data_.items():
        iterations = list(values.keys())  # X-axis (iterations)
        costs = list(values.values())  # Y-axis (costs)

        plt.plot(iterations, costs, marker='', label=f'Opt {opt}')

    # Labels and title
    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.title('Cost vs Iteration for Different #Opt')

    plt.ylim(6750,8000)
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()

