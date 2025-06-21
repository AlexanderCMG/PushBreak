import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import scipy.stats as stats


def import_data():
    file_path = "csv/PushBreak_June+20,+2025_01.58.csv"
    df_raw = pd.read_csv(file_path)
    question_labels = df_raw.iloc[0]

    df_responses = df_raw.iloc[2:].reset_index(drop=True)
    df_responses.columns = question_labels

    df_responses = df_responses.loc[:, ~df_responses.columns.str.contains(
        'Unnamed|Response ID|Recipient|Start Date|End Date|Response Type|Progress|Duration|Finished|Recorded|Location|UserLanguage|IP Address|External Data Reference|Distribution Channel|User Language|Do you agree to the details set out in the consent form?',
        case=False
    )]

    question_data = {}

    for question in df_responses.columns:
        values = df_responses[question].tolist()

        # Try to convert to numeric, keeping original values if conversion fails
        converted_values = []
        for val in values:
            if pd.isna(val) or val == '' or val is None:
                converted_values.append(np.nan)
            else:
                try:
                    # Try to convert to int first
                    if isinstance(val, str) and val.strip().replace('-', '').isdigit():
                        converted_values.append(int(val))
                    # Try to convert to float if it has decimal points
                    elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                        float_val = float(val)
                        # Convert to int if it's a whole number
                        converted_values.append(int(float_val) if float_val.is_integer() else float_val)
                    else:
                        # Try pandas numeric conversion as fallback
                        numeric_val = pd.to_numeric(val, errors='coerce')
                        if pd.isna(numeric_val):
                            converted_values.append(val)  # Keep original string
                        else:
                            converted_values.append(int(numeric_val) if numeric_val == int(numeric_val) else numeric_val)
                except (ValueError, TypeError):
                    converted_values.append(val)  # Keep original value if conversion fails

        # Convert to numpy array
        question_data[question] = np.array(converted_values)

    return question_data

def make_categories():
    categories = {
        "introduction": ["Participant number", "What is your age?", "What is your gender?", "How many hours a day do you normally spend sitting? - Hours", "Have you ever used a footrest while working or studying?", "Have you used any time management apps or timers to remind you to take breaks?", "Do you have any experience using the Pomodoro technique for working or studying?"],
        "usability": ["I found PushBreak easy to use", "I felt confident using PushBreak", "I found PushBreak unnecessarily complex", "I think most people would learn to use PushBreak very quickly", "I needed to learn a lot of things before I could get going with PushBreak"],
        "nudging": ["I noticed when the nudging from PushBreak started", "I felt the urge to move or get up at the right time", "The nudging of the device was…", "The shape-changing feedback clearly signalled that it was time to take a break", "The timing of the nudges was appropriate for my workflow"],
        "effectiveness": ["PushBreak helped me become more aware of how long I had been sitting",
                          "PushBreak encouraged me to take breaks",
                          "I would be more likely to take micro-breaks if I used PushBreak regularly",
                          "I felt that PushBreak successfully changed my behaviour",
                          "I felt that PushBreak was more effective than a timer"],
        "integration": ["PushBreak felt like a natural part of my workspace", "PushBreak supported my workflow rather than interrupting it", "PushBreak's physical presence and feedback were well integrated into the environment"],
        "acceptance": ["I would consider using a similar device in my workspace", "I would choose PushBreak over a conventional timer", "Using PushBreak made me feel more responsible about my health", "I would like to use PushBreak regularly"]
    }

    return categories

def print_category(data, category_name, category_questions):
    print(f"\n=== {category_name.upper()} ===")
    for question in category_questions:
        if question in data:
            print(f"{question}: {data[question]}\n")

def category_average(data, category_name, category_questions):
    # Add all the columns of every question in the category
    category_average_per_participant = np.mean([data[question] for question in category_questions if question in data], axis=0)
    return category_average_per_participant

# def create_bar_scatter_plots(graph_data, categories_to_analyze):
#     """
#     Create 4 bar charts with scatter plots overlaid showing average per category using Seaborn
#     """
#     # Set up the color palette
#     palette = sb.color_palette("colorblind")
#     blue = palette[0]
#     orange = palette[1]
#     green = palette[2]
#     red = palette[3]
#     purple = palette[4]
#     brown = palette[5]
#     pink = palette[6]
#     grey = palette[7]
#     yellow = palette[8]
#     teal = palette[9]

#     # Category colors - blue as main, with variety for each category
#     category_colors = [blue, green, purple, teal]

#     # Set seaborn style
#     sb.set_style("whitegrid")
#     fig, axes = plt.subplots(2, 2, figsize=(15, 12))
#     axes = axes.flatten()

#     for i, (category_name, category_data) in enumerate(zip(categories_to_analyze, graph_data)):
#         ax = axes[i]

#         # Remove NaN values for plotting
#         clean_data = category_data[~np.isnan(category_data)]

#         if len(clean_data) == 0:
#             ax.text(0.5, 0.5, f'No data available\nfor {category_name}',
#                    ha='center', va='center', transform=ax.transAxes, fontsize=12)
#             ax.set_title(category_name.capitalize(), fontsize=14, fontweight='bold')
#             continue

#         # Calculate statistics
#         mean_value = np.mean(clean_data)
#         std_value = np.std(clean_data)

#         # Create bar chart using seaborn
#         sb.barplot(x=[category_name.capitalize()], y=[mean_value],
#                   color=category_colors[i], alpha=0.8, ax=ax,
#                   errorbar=None)  # We'll add custom error bars

#         # Add custom error bars with red color
#         ax.errorbar([0], [mean_value], yerr=[std_value], fmt='none',
#                    color=red, capsize=8, capthick=2, linewidth=2)

#         # Create scatter plot overlay using seaborn
#         participant_indices = np.zeros(len(clean_data)) + np.random.normal(0, 0.08, len(clean_data))
#         sb.scatterplot(x=participant_indices, y=clean_data, color=red, alpha=0.7,
#                       s=60, ax=ax, zorder=5)

#         # Customize the plot
#         ax.set_xlim(-0.5, 0.5)
#         ax.set_ylim(0, 8)
#         ax.set_ylabel('Rating', fontsize=12, fontweight='bold')
#         ax.set_xlabel('')
#         ax.set_title(category_name.capitalize(), fontsize=14, fontweight='bold',
#                     color=category_colors[i])

#         # Add statistics text with styled box
#         stats_text = f'Mean: {mean_value:.2f}\nSD: {std_value:.2f}\nN: {len(clean_data)}'
#         ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
#                 verticalalignment='top', fontsize=11, fontweight='bold',
#                 bbox=dict(boxstyle='round,pad=0.5', facecolor=category_colors[i],
#                          alpha=0.2, edgecolor=red, linewidth=1.5))

#     plt.tight_layout()
#     plt.suptitle('PushBreak Survey Results: Category Averages with Individual Responses',
#                 fontsize=16, fontweight='bold', y=1.02, color=blue)
#     plt.show()

def create_combined_comparison_plot(graph_data, categories_to_analyze, p_values):
    """
    Create a single plot comparing all categories using Seaborn
    """
    # Set up the color palette
    palette = sb.color_palette("colorblind")
    blue = palette[0]
    orange = palette[1]
    green = palette[2]
    red = palette[3]
    purple = palette[4]
    brown = palette[5]
    pink = palette[6]
    grey = palette[7]
    yellow = palette[8]
    teal = palette[9]

    # Category colors - going crazy with the palette!
    category_colors = [red, yellow, green, teal, purple]

    # Set seaborn style
    sb.set_style("white")
    plt.figure(figsize=(14, 8))

    # Calculate means and standard deviations
    means = []
    stds = []
    clean_data_sets = []

    for category_data in graph_data:
        clean_data = category_data[~np.isnan(category_data)]
        clean_data_sets.append(clean_data)
        if len(clean_data) > 0:
            means.append(np.mean(clean_data))
            stds.append(np.std(clean_data))
        else:
            means.append(0)
            stds.append(0)

    # Create bar chart using seaborn
    x_pos = np.arange(len(categories_to_analyze))
    category_names = [cat.capitalize() for cat in categories_to_analyze]

    # Create the bar plot
    bars = sb.barplot(x=category_names, y=means, palette=category_colors, alpha=0.8,
                      edgecolor=grey, linewidth=1)

    # Add custom error bars with red color
    plt.errorbar(x_pos, means, yerr=stds, fmt='none', color=grey,
                capsize=8, capthick=3, linewidth=2, zorder=10)

    plt.axhline(y=4, color=grey, linewidth=1, linestyle='--', zorder=1)

    # Add scatter plots for each category with different colors]
    for i, clean_data in enumerate(clean_data_sets):
        if len(clean_data) > 0:
            # Create a temporary DataFrame for this category
            temp_df = pd.DataFrame({
                'Category': [category_names[i]] * len(clean_data),
                'Value': clean_data
            })
            sb.swarmplot(x="Category", y="Value", data=temp_df, color=blue, alpha=0.9
                         , size=10, zorder=5)

            # Add p-values as text annotations above the bars
            p_value = p_values[i]
            if p_value < 0.001:
                p_text = 'p < 0.001'
            else:
                p_text = f'p = {p_value:.3f}'

            plt.text(i, 7.2, p_text,
                     ha='center', va='bottom',
                     fontsize=14, color="black",
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              alpha=0.8, edgecolor=purple, linewidth=1))

    # Customize the plot
    plt.xlabel('Categories', fontsize=16, fontweight='bold')
    plt.ylabel('Average rating', fontsize=16, fontweight='bold')
    # plt.title('PushBreak Survey Results: Comparison Across Categories',
    #          fontsize=16, fontweight='bold', color=blue, pad=20)
    plt.ylim(1, 7.5)

    # Add value labels on bars with different colors
    # label_colors = [grey, brown, pink, teal, red]
    # for i, (mean, std) in enumerate(zip(means, stds)):
    #     plt.text(i, mean + std + 0.15, f'{mean:.2f}',
    #             ha='center', va='bottom', fontweight='bold',
    #             fontsize=12, color=label_colors[i],
    #             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
    #                      alpha=0.8, edgecolor=red, linewidth=1))


    plt.tight_layout()
    plt.savefig("plots/survey_data.png", dpi=600, bbox_inches='tight')

def statistics(data, categories):
    print(data)
    p_values = []

    for i in range(len(data)):
        _, p_value = stats.shapiro(data[i])

        if p_value < 0.05:
            print(f"Category '{categories[i]}' does not follow a normal distribution p={p_value}.")
            _, p = stats.wilcoxon(data[i], np.full(len(data[i]), 4))
            print(f"Wilcoxon signed-rank test p-value for '{categories[i]}': {p}")
        else:
            print(f"Category '{categories[i]}' follows a normal distribution p={p_value}.")
            _, p = stats.ttest_1samp(data[i], 4)
            print(f"One-sample t-test p-value for '{categories[i]}': {p}")

        p_values.append(p)
    print(f"P-values for each category: {p_values}")

    return p_values

def main():
    data = import_data()
    categories = make_categories()

    # Reverse negatively worded questions in usability
    if categories["usability"][2] in data:
        data[categories["usability"][2]] = 8 - data[categories["usability"][2]]
    if categories["usability"][4] in data:
        data[categories["usability"][4]] = 8 - data[categories["usability"][4]]

    if categories["nudging"][2] in data:
        # Create a mapping dictionary
        nudging_mapping = {
            "Too subtle": 1,
            "A little subtle": 4,
            "Just right": 7,
            "A little obvious": 4,
            "Too obvious": 1
        }

        # Convert the numpy array to handle string replacements
        nudging_data = data[categories["nudging"][2]]
        converted_data = []

        for value in nudging_data:
            if pd.isna(value) or value == '' or value is None:
                converted_data.append(np.nan)
            elif value in nudging_mapping:
                converted_data.append(nudging_mapping[value])
            else:
                # Keep original value if it's already numeric or unknown string
                try:
                    converted_data.append(float(value))
                except (ValueError, TypeError):
                    converted_data.append(np.nan)

        data[categories["nudging"][2]] = np.array(converted_data)

    # For each category except introduction, average for each participant their answers
    categories_to_analyze = ["usability", "nudging", "effectiveness", "integration", "acceptance"]

    graph_data = []
    for category_name in categories_to_analyze:
        category_avg = category_average(data, category_name, categories[category_name])
        graph_data.append(category_avg)

    # Create the visualizations
    # create_bar_scatter_plots(graph_data, categories_to_analyze)
    p_values = statistics(graph_data, categories_to_analyze)

    create_combined_comparison_plot(graph_data, categories_to_analyze, p_values)

if __name__ == "__main__":
    main()