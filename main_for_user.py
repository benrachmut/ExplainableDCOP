import math
import pickle
import tkinter as tk

from Globals_ import *
from tkinter import ttk, messagebox

from XDCOPS import *
# Example choices for DCOP type and Algorithm
from enums import DcopType, Algorithm
from problems import *
import plotly.graph_objects as go




def get_DCOP(i,algorithm,dcop_type,A = 50):
    if dcop_type == DcopType.sparse_random_uniform:
        return DCOP_RandomUniform(i, A, sparse_D, "Sparse Uniform", algorithm,sparse_p1)
    if dcop_type == DcopType.dense_random_uniform:
        return DCOP_RandomUniform(i, A, dense_D, "Dense Uniform", algorithm,dense_p1)
    if dcop_type == DcopType.graph_coloring:
        return DCOP_GraphColoring(i, A,graph_coloring_D, "Graph Coloring", algorithm)
    if dcop_type == DcopType.meeting_scheduling:
        return DCOP_MeetingSchedualing(id_=i, A=A, meetings=meetings, meetings_per_agent=meetings_per_agent,
                                        time_slots_D=time_slots_D, dcop_name="Meeting Schedualing",
                                       algorithm = algorithm)


def get_dcop_and_solve():
    dcop = get_DCOP(seed_dcop, algorithm, dcop_type, A)
    if is_center_solver:
        dcop.execute_center()
    else:
        dcop.execute_distributed()
    return dcop


def create_x_standard_dcop():
    query = QueryGenerator(dcop, seed_query, num_variables, num_values, with_connectivity_constraint).get_query()

    return XDCOP(dcop, query)

def create_x_MeetingSchedualing_dcop():
    qg = QueryGeneratorScheduling(dcop, seed_query, num_meetings, num_alternative_slots, with_connectivity_constraint)
    query =qg.get_query()
    return XDCOP(dcop, query)


def create_curves(ys,extra_infos,con_collections):
    curves = []
    for i in range(len(ys)):
        y = ys[i]
        infos = extra_infos[i]
        name = con_collections[i]
        curves.append({"y": y, "info": infos, "name": name})
    return curves

def create_graph_ui(x,ys,extra_infos,con_collections,y_title,title):
    curves = create_curves(ys,extra_infos,con_collections)

    # Create the figure
    fig = go.Figure()

    # Add curves in a loop
    for curve in curves:
        fig.add_trace(go.Scatter(
            x=x,
            y=curve["y"],
            mode='lines+markers',
            hovertemplate='<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>Info:</b> %{text}',
            text=curve["info"],
            name=curve["name"]
        ))

    # Customize the layout
    fig.update_layout(
        title=title,
        xaxis_title="Constraint Count",
        yaxis_title=y_title,
        template="plotly_white",
        legend_title="PA"
    )



    fig.write_html(title.replace(":", "_")+".html")



def get_data_for_cum_delta_from_sol(x_dcop,title):
    cum_delta_from_solution_dict = x_dcop.explanation.cum_delta_from_solution_dict
    sum_of_alternative_cost_dict = x_dcop.explanation.sum_of_alternative_cost_dict
    con_collections = []
    ys_sum_of_alternative = []
    ys_cum_delta = []
    extra_infos = []

    inf_constraint_flag = False
    for con_collection,dict_ in cum_delta_from_solution_dict.items():
        x = []
        counter = 0
        con_collections.append(con_collection.__str__())
        extra_info = []
        y_cum_delta = []
        y_sum_of_alternative=[]
        for constraint, value in dict_.items():
            if constraint.cost == my_inf:
                inf_constraint_flag = True
            x.append(counter)
            counter += 1
            y_cum_delta.append(value)
            y_sum_of_alternative.append(sum_of_alternative_cost_dict[con_collection][constraint])
            extra_info.append(constraint.__str__())
        ys_cum_delta.append(y_cum_delta)
        ys_sum_of_alternative.append(y_sum_of_alternative)
        extra_infos.append(extra_info)

    is_y_log = inf_constraint_flag
    y_title = "Cumulative Δ Cost"

      # Controls the rate of decay


    #if is_y_log:
        #alpha = 0.1
        #ys_cum_delta = [[math.copysign(1 - math.exp(-alpha * abs(num)), num) for num in sublist] for sublist
         #                         in
         #                         ys_cum_delta]
        #ys_sum_of_alternative = [[math.copysign(1 - math.exp(-alpha * abs(num)), num) for num in sublist] for sublist
        #                          in
        #                          ys_sum_of_alternative]
        #y_title = f"Exponential Decay Transform (alpha={alpha}) of {y_title}"

    create_graph_ui( x=x,ys=ys_cum_delta,extra_infos=extra_infos,con_collections=con_collections, y_title=y_title,title = title+"__")
    # Save the figure as a PDF file (optional)
    #print()

def get_name_of_exp(A, property="complete"):
    return str(dcop_type.name) + "_" + property + "_agents" + str(A)

def get_pickle_name(A, property="complete"):
    return get_name_of_exp(A, property) + ".pkl"


def get_dcops(A, property= "complete"):
    pickle_name = get_pickle_name(A, property)
    with open(pickle_name, "rb") as file:
        return pickle.load(file)


if __name__ == '__main__':
    ######################--------------------######################
    seed_dcop=1
    A = 4
    dcop_type = DcopType.meeting_scheduling
    title = "A:"+str(A)+",dcop:"+str(dcop_type.name)+","
    is_center_solver = True
    try:
        dcop = get_dcops(A=A, property="complete")[0]
    except:
        dcop = get_dcop_and_solve()

    # XDCOP
    seed_query=1
    with_connectivity_constraint = True
    if isinstance(dcop,DCOP_MeetingSchedualing) and special_generator_for_MeetingScheduling:
        num_meetings = 2
        num_alternative_slots = 2
        x_dcop = create_x_MeetingSchedualing_dcop()
        title += "meetings:"+str(num_meetings)+",alt_slots:"+str(num_alternative_slots)
    else:
        num_variables = 2
        num_values = 2
        x_dcop = create_x_standard_dcop()
        title += "vars:"+str(num_variables)+"_values:"+str(num_values)

    # XDCOP - scheduling
    # explanation presentation
    get_data_for_cum_delta_from_sol(x_dcop,title)

    # Sample data








