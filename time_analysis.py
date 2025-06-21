import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb

# Read the CSV file
df = pd.read_csv('csv\sitting_times.csv')

# Convert timestamp columns to datetime
df['first_session_start'] = pd.to_datetime(df['first_session_start'])
df['last_session_end'] = pd.to_datetime(df['last_session_end'])

# Calculate duration for each participant
df['duration_seconds'] = (df['last_session_end'] - df['first_session_start']).dt.total_seconds()
df['duration_minutes'] = df['duration_seconds'] / 60

# Function to format duration as minutes and seconds
def format_duration(total_seconds):
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes}m {seconds}s"

# NumPy array of durations in seconds
TIME_TILL_NUDGE = 330
duration_array = np.array(df['duration_seconds'] - TIME_TILL_NUDGE)

for participant in range(len(duration_array)):
    print(f"Participant {participant + 1}: {format_duration(duration_array[participant])}")

# Calculate statistics
# =======================================
# The mean duration
mean_duration = np.mean(duration_array)

# Standard deviation of the durations
std_duration = np.std(duration_array)

# Confidence interval for the mean duration
def confidence_interval(data):
    n = len(data)
    mean = np.mean(data)
    se = np.std(data, ddof=1) / np.sqrt(n)  # Standard error
    h = se * 1.96  # Z-score for 95% confidence
    return mean - h, mean + h

ci_lower, ci_upper = confidence_interval(duration_array)

# Print statistics
print(f"Mean duration: {format_duration(mean_duration)}")
print(f"Standard deviation: {format_duration(std_duration)}")
print(f"95% Confidence interval: {format_duration(ci_lower)} - {format_duration(ci_upper)}")
print(f"Number of participants: {len(duration_array)}")

# Create the vertical boxplot using seaborn
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


plt.figure(figsize=(8, 10))
sb.boxplot(y=duration_array/60, color=blue, width=0.5)

# Customize the plot
plt.title('Time spent seated after first nudge', fontsize=24, fontweight='bold')
plt.ylabel('Duration (minutes)', fontsize=16)
plt.grid(True, alpha=0.3)
max_y = np.max(duration_array) / 60
plt.xticks([])
plt.yticks(range(0, int(max_y) + 2, 1))
plt.ylim(bottom=0)

# Add statistical annotations
plt.axhline(y=mean_duration/60, color=red, linestyle='--', alpha=0.8, label=f'Mean: {format_duration(mean_duration)}')
plt.axhline(y=ci_lower/60, color=orange, linestyle=':', alpha=0.8, label=f'95% CI Lower: {format_duration(ci_lower)}')
plt.axhline(y=ci_upper/60, color=orange, linestyle=':', alpha=0.8, label=f'95% CI Upper: {format_duration(ci_upper)}')

plt.legend(loc='upper right', fontsize=12)
plt.tight_layout()

# Save the plot as a PNG file
plt.savefig("plots/time_seated.png", dpi=600, bbox_inches='tight')
