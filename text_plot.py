import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
import scipy.stats as stats

# Read the CSV file
df = pd.read_csv('csv/participant_cpm_results.csv')

# Melt the dataframe to long format for plotting
df_melted = df.melt(id_vars=['participant_id'],
                    value_vars=['session_1_cpm', 'session_2_cpm', 'session_3_cpm',
                               'session_4_cpm', 'session_5_cpm', 'session_6_cpm'],
                    var_name='session', value_name='cpm')

# Extract session number from session column
df_melted['session_num'] = df_melted['session'].str.extract('(\d+)').astype(int)


# Testing for normality of CPM data
statistic, p_value = stats.shapiro(df_melted['cpm'])

if p_value > 0.05:
    print("The CPM data is normally distributed (p > 0.05).")
else:
    print("The CPM data is not normally distributed (p <= 0.05).")


correlation = df_melted['session_num'].corr(df_melted['cpm'], method='kendall')
print(f"Correlation between session number and CPM: {correlation:.3f}")

p = stats.kendalltau(df_melted['session_num'], df_melted['cpm']).pvalue
print(f"P-value for the correlation: {p:.3f}")
if p < 0.05:
    print(f"The correlation is statistically significant (p < 0.05).")
else:
    print(f"The correlation is not statistically significant (p >= 0.05).")


# Set up the plot style
plt.style.use('default')
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


# Create the figure
fig, ax = plt.subplots(figsize=(12, 8))

# Create the scatter plot with regression line and confidence interval
sb.regplot(data=df_melted, x='session_num', y='cpm',
            scatter_kws={'alpha': 0.7, 's': 60, 'color': blue},
            line_kws={'color': red, 'linewidth': 2},
            ci=95, ax=ax)

# Customize the plot
ax.set_xlabel('Session Number', fontsize=14, fontweight='bold')
ax.set_ylabel('Characters per minute (CPM)', fontsize=14, fontweight='bold')
# ax.set_title('CPM Performance Across Sessions\nwith Linear Regression and 95% Confidence Interval',
#              fontsize=16, fontweight='bold', pad=20)

# Set x-axis ticks to show all sessions
ax.set_xticks(range(1, 7))
ax.set_xticklabels([str(i) for i in range(1, 7)])

# # Add grid for better readability
# ax.grid(True, alpha=0.3, linestyle='--')

# Add statistics box
stats_text = f'τ = {correlation:.3f}\np = {p:.3f}'
if p < 0.001:
    stats_text = f'τ = {correlation:.3f}\np < 0.001'

# Create text box with statistics
textstr = stats_text
props = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor=purple)
ax.text(0.87, 0.95, textstr, transform=ax.transAxes, fontsize=16,
        verticalalignment='top', bbox=props)

# Improve layout
plt.tight_layout()


# Show the plot
plt.savefig('plots/typing_performance.png', dpi=600)
