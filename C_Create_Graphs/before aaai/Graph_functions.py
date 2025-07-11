import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from enums import QueryType, CommunicationType

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
    "Shortest_Explanation": r"CEDAR$(O_1)$",
    "Sort_Parallel": r"CEDAR$(O_2)$",
    "Sort_Parallel_Not_Opt": r"CEDAR$(V_1)$",
    "Varint_max": r"CEDAR$(V_2)$"
}



selected_communication_and_new_name = {
    CommunicationType.BFS.name: "BFS",
    CommunicationType.Broadcast_Total.name: "BB",
    CommunicationType.Broadcast.name: "UB",
}

measure_new_names = {
    "agent_privacy_normalized": "Agent Privacy",
    "topology_privacy_normalized": "Topology Privacy",
    "constraint_privacy_normalized": "Constraint Privacy",
    "decision_privacy_with_send_sol_normalized": "Decision Privacy",
    "decision_privacy_without_send_sol_constraint_normalized": "Decision Privacy",

    "agent_privacy": "Agent Privacy",
    "topology_privacy": "Topology Privacy",
    "constraint_privacy": "Constraint Privacy",

    "decision_privacy_with_send_sol_constraint": "Decision Privacy",
    "decision_privacy_without_send_sol_constraint": "Decision Privacy"
}

colors_explanation_algos = {


"CEDAR":  "chocolate",
r"CEDAR$(O_1)$": "red",
r"CEDAR$(O_2)$": 'blue',
r"CEDAR$(V_1)$": 'black',
r"CEDAR$(V_2)$": "green"
}
line_styles = {'Next Best': '-', 'Random': '--', }

colors_dcop_algos = {'Optimal': 'blue', '1-Opt': 'red'}


def get_folder_to_save_figure_name(graph_type, prob, selected_density):
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
            folder_to_save = prob + "_" + "dense"

        if selected_density == 0.2:
            figure_name = graph_type + "_" + prob + "_" + "sparse"
            folder_to_save = prob + "_" + "sparse"

    return folder_to_save, figure_name


class ColorsInGraph:
    dcop_algorithms = 1
    explanation_algorithms = 2



import matplotlib.pyplot as plt


def create_combined_privacy_graph_with_first_legend_only(data_list, titles_list, x_label, y_label, folder_to_save, figure_name):
    # Define the font sizes and line width
    axes_titles_font = 14
    tick_font_size = 14
    linewidth = 2

    # Create a 2x2 grid of subplots (adjust as necessary)
    fig, axes = plt.subplots(2, 2, figsize=(8,6))  # Adjust the size based on your preference
    axes = axes.flatten()  # Flatten the 2D array of axes to make iteration easier

    # Loop over the data, axes, and titles, plotting each graph in its respective subplot
    letters = ["(a)","(b)","(c)","(d)"]
    for i, (data, ax, title) in enumerate(zip(data_list, axes, titles_list)):
        # Plot all communication types from the dataset in this subplot
        for comm_type, xy_values in data.items():
            x_values = list(xy_values.keys())
            y_values = list(xy_values.values())
            line, = ax.plot(x_values, y_values, marker='o', linewidth=linewidth)

        # Set labels and title for this subplot
        ax.set_xlabel(x_label, fontsize=axes_titles_font)
        ax.set_ylabel(titles_list[i], fontsize=axes_titles_font)
        ax.set_title(letters[i], fontsize=axes_titles_font)  # Set title from titles_list

        # Set tick font size
        ax.tick_params(axis='both', labelsize=tick_font_size)

        # Add grid to each subplot
        ax.grid(True)

    # Add the legend only for the first subplot (i=0)
    # Collect the lines and labels from the first subplot
    first_subplot_lines = [line for line, _ in zip(axes[0].get_lines(), data_list[0].keys())]
    first_subplot_labels = [comm_type for comm_type in data_list[0].keys()]

    # Add a single horizontal legend at the top of the figure
    fig.legend(first_subplot_lines, first_subplot_labels, loc='upper center',
               ncol=len(first_subplot_labels), fontsize=10, bbox_to_anchor=(0.5, 1),
               borderpad=0.5, handlelength=2, frameon=False)

    # Adjust layout to avoid overlap
    plt.tight_layout()

    # Save the combined figure with subplots
    fig.savefig(f"{folder_to_save}/{figure_name}.pdf", format="pdf", bbox_inches='tight')
    plt.close(fig)


def create_privacy_graph(data, x_label, y_label, folder_to_save, figure_name):
    # Define the font sizes and line width
    linewidth = 2

    # Create main figure without a legend
    fig, ax = plt.subplots(figsize=(4, 3))

    # Store legend elements
    lines = []
    labels = []

    # Plot each communication type
    for comm_type, xy_values in data.items():
        x_values = list(xy_values.keys())
        y_values = list(xy_values.values())
        line, = ax.plot(x_values, y_values, marker='o', linewidth=linewidth)
        lines.append(line)
        labels.append(comm_type)

    # Set the labels with the specified font size
    ax.set_xlabel(x_label, fontsize=axes_titles_font)
    ax.set_ylabel(y_label, fontsize=axes_titles_font)

    # Set tick font size
    ax.tick_params(axis='both', labelsize=tick_font_size)

    # Save the main figure (without legend)
    fig.savefig(f"{folder_to_save}/{figure_name}.pdf", format="pdf", bbox_inches='tight')
    plt.close(fig)

    # Create standalone legend figure with a horizontal layout
    legend_fig = plt.figure(figsize=(6, 1))  # Adjust width to fit all labels in a row
    legend_ax = legend_fig.add_subplot(111)
    legend_ax.axis("off")  # Hide axes
    legend_fig.legend(lines, labels, fontsize=legend_font_size, loc="center", ncol=len(lines),
                      frameon=False)  # Horizontal legend without frame

    # Save the legend as a separate PDF
    legend_fig.savefig(f"{folder_to_save}/8_{folder_to_save}_legend.pdf", format="pdf", bbox_inches='tight')
    plt.close(legend_fig)


def create_single_graph(is_with_legend, data, colors_type, curve_widths, x_name, y_name, folder_to_save, figure_name,
                        manipulate_y=False, x_min=None, x_max=None, y_min=None, y_max=None,
                        is_highlight_horizontal=False, x_ticks=None, with_points=True, horizontal_width=10,
                        horizontal_alpha=0.5, horizontal_location=1, create_legend_image=False):
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
        # line_legend = [Line2D([0], [0], color='black', linestyle=line_styles[key], lw=2, label=key) for key in line_styles]

        # Place line type legend
        # plt.legend(handles=color_legend, title="", loc="center left", bbox_to_anchor=(1.02, 0.5),
        #           borderaxespad=0., frameon=False, labelspacing=0.3)
        plt.legend(handles=color_legend, title="", loc="best",  # 'best' places it in the least obstructive area
                   frameon=True, labelspacing=0.3, fontsize=legend_font_size, title_fontsize=12)
        # Place algorithm color legend
        # plt.legend(handles=color_legend, title="Algorithm", loc="center left", bbox_to_anchor=(1.02, 0.3), borderaxespad=0.,
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
        plt.axhline(horizontal_location, color='black', linewidth=horizontal_width, linestyle='-',
                    alpha=horizontal_alpha, label='y = 1', zorder=0)

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
        figure_name = "noLegend_" + figure_name
    plt.savefig(f"{folder_to_save}/{figure_name}.pdf", format="pdf", bbox_inches='tight')
    # plt.savefig(f"{folder_to_save}/{figure_name}.jpeg", format="jpeg", bbox_inches='tight')

    # Clear the plot
    plt.clf()
