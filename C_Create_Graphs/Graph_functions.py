import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from enums import QueryType

# Define line styles and colors for subkeys
axes_titles_font = 10
axes_number_font = 10
legend_font_size = 8
tick_font_size = 10
linewidth = 3

selected_query_types_and_new_name = {QueryType.educated.name: "Next Best", QueryType.rnd.name: "Random"}

selected_algos_and_new_name = {"Complete": "Optimal", "One_Opt": "1-Opt"}

selected_explanations_and_new_name = {
    "Grounded_Constraints": "CEDAR",
    "Shortest_Explanation": "CEDAR(O1)",
    "Sort_Parallel": "CEDAR(O2)",
    "Sort_Parallel_Not_Opt": "CEDAR(V1)",
    "Varint_max": "CEDAR(V2)"
}


colors_explanation_algos = {
    "CEDAR":"chocolate" ,
    "CEDAR(O1)": "red",
    "CEDAR(O2)":'blue' ,
    "CEDAR(V1)":'black',
    "CEDAR(V2)": "green"
}
line_styles = {'Next Best': '-', 'Random': '--', }

colors_dcop_algos = {'Optimal': 'blue', '1-Opt': 'red'}


def get_folder_to_save_figure_name(graph_type, prob,selected_density):
    figure_name = graph_type + "_" + prob

    if prob == "meeting_scheduling":

        if selected_density == 0.7:
            figure_name = figure_name + "_" + "07_dense"
            folder_to_save = prob + "_" + "07_dense"

        if selected_density == 0.5:
            figure_name = graph_type + "_" + prob + "_" + "05_dense"
            folder_to_save = prob + "_" + "05_dense"

        if selected_density == 0.2:
            figure_name = graph_type + "_" + prob + "_" + "02_dense"
            folder_to_save = prob + "_" + "02_dense"

    if prob == "random":
        if selected_density == 0.7:
            figure_name = figure_name + "_" + "dense"
            folder_to_save =  prob + "_" + "dense"

        if selected_density == 0.2:
            figure_name = graph_type + "_" + prob + "_" + "sparse"
            folder_to_save =  prob + "_" + "sparse"

    return folder_to_save, figure_name

class ColorsInGraph:
    dcop_algorithms = 1
    explanation_algorithms = 2

def create_single_graph(is_with_legend,data,colors_type,curve_widths,x_name,y_name,folder_to_save,figure_name,manipulate_y=False, x_min = None,x_max=None,y_min=None,y_max=None,is_highlight_horizontal=False,x_ticks = None,with_points = True,horizontal_width = 10, horizontal_alpha = 0.5,horizontal_location = 1,create_legend_image = False):
    plt.figure(figsize=(4, 3))
    if colors_type == ColorsInGraph.dcop_algorithms:
        colors = colors_dcop_algos
    if colors_type == ColorsInGraph.explanation_algorithms:
        colors = colors_explanation_algos

    for primary_key, sub_dict in data.items():
        for sub_key, values in sub_dict.items():
            x = list(values.keys())  # X-axis values
            y = list(values.values())  # Y-axis values
            if manipulate_y:


                plt.yscale('symlog', linthresh=1)  # Linear threshold near zero

            dynamic_linewidth = curve_widths.get(sub_key, 2)  # Default line width is 2

            # Plot the line with transparency
            plt.plot(x, y, linewidth=dynamic_linewidth, linestyle=line_styles[primary_key],
                     color=colors[sub_key], alpha=0.5,  # Adjust line transparency
                     label=f"{sub_key} ({primary_key})")

            # Add data points as semi-transparent circles
            point_size = dynamic_linewidth * 20
            if with_points:
                plt.scatter(x, y, color=colors[sub_key],
                            alpha=0.5, s=point_size, zorder=5)  # # Adjust point transparency

    # Add labels, title, and legends
    plt.xlabel(x_name, fontsize=axes_titles_font)
    plt.ylabel(y_name, fontsize=axes_titles_font)

    # Custom legends
    if is_with_legend:
        color_legend = [Line2D([0], [0], color=colors[key], lw=2, label=key) for key in colors]
        #line_legend = [Line2D([0], [0], color='black', linestyle=line_styles[key], lw=2, label=key) for key in line_styles]

        # Place line type legend
        #plt.legend(handles=color_legend, title="", loc="center left", bbox_to_anchor=(1.02, 0.5),
        #           borderaxespad=0., frameon=False, labelspacing=0.3)
        plt.legend(handles=color_legend, title="", loc="best",  # 'best' places it in the least obstructive area
                   frameon=True, labelspacing=0.3, fontsize=legend_font_size, title_fontsize=12)
        # Place algorithm color legend
        #plt.legend(handles=color_legend, title="Algorithm", loc="center left", bbox_to_anchor=(1.02, 0.3), borderaxespad=0.,
        #           frameon=False, labelspacing=0.3)  #

        # Optionally create a separate legend image
        if create_legend_image:
            if create_legend_image:
                plt.figure(figsize=(10, 1))  # New figure for the legend (wider for horizontal display)
                plt.legend(handles=color_legend, title="", loc="center", frameon=False,
                           fontsize=legend_font_size, title_fontsize=12, ncol=len(colors))  # ncol set to total items
                plt.axis('off')  # Remove axes for clean legend image
                plt.tight_layout()
                plt.savefig(f"{folder_to_save}/legend_image.pdf", format="pdf", bbox_inches='tight')
                plt.close()  # Close the legend image figure to avoid it being displayed along with the main plot

    if is_highlight_horizontal:
        plt.axhline(horizontal_location, color='black', linewidth=horizontal_width , linestyle='-', alpha=horizontal_alpha, label='y = 1', zorder=0)

    # Add grid, limits, and improve layout
    plt.grid(True)
    if y_min != None:
        plt.ylim(y_min, y_max)
    if x_min != None:
        plt.xlim(x_min, x_max)
    plt.tick_params(axis='both', which='major', labelsize=tick_font_size)
    plt.tight_layout(pad=1.0)

    # Set ticks on the x-axis at every 1 unit
    plt.xticks(ticks=x_ticks)  # Assuming x-axis range is from 1 to 10

    # Add grid with a line at every tick
    plt.grid(axis='x', which='major', linestyle='-', color='gray', alpha=0.7)  # Customize the grid style


    # Save the plot
    if not is_with_legend:
        figure_name = "noLegend_"+figure_name
    plt.savefig(f"{folder_to_save}/{figure_name}.pdf", format="pdf", bbox_inches='tight')
    #plt.savefig(f"{folder_to_save}/{figure_name}.jpeg", format="jpeg", bbox_inches='tight')

    # Clear the plot
    plt.clf()
