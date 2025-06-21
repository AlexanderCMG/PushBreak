import pandas as pd
import numpy as np


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

    # for key, value in question_data.items():
    #     print(f"{key}: {value}")

    return question_data

def make_categories():
    introduction = ["Participant number", "What is your age?", "What is your gender?", "How many hours a day do you normally spend sitting? - Hours", "Have you ever used a footrest while working or studying?", "Have you used any time management apps or timers to remind you to take breaks?", "Do you have any experience using the Pomodoro technique for working or studying?"]
    usability = ["I found PushBreak easy to use", "I felt confident using PushBreak", "I found PushBreak unnecessarily complex", "I think most people would learn to use PushBreak very quickly", "I needed to learn a lot of things before I could get going with PushBreak"]
    nudging = ["I noticed when the nudging from PushBreak started", "I felt the urge to move or get up at the right time", "The nudging of the device was…", "The shape-changing feedback clearly signalled that it was time to take a break", "The timing of the nudges was appropriate for my workflow"]
    effectiveness = ["PushBreak helped me become more aware of how long I had been sitting", "PushBreak encouraged me to take breaks", "I would be more likely to take micro-breaks if I used PushBreak regularly", "I felt that PushBreak successfully changed my behaviour", "I felt that PushBreak was more effective than a timer"]
    integration = ["PushBreak felt like a natural part of my workspace", "PushBreak supported my workflow rather than interrupting it", "PushBreak's physical presence and feedback were well integrated into the environment"]
    acceptance = ["I would consider using a similar device in my workspace", "I would choose PushBreak over a conventional timer", "Using PushBreak made me feel more responsible about my health", "I would like to use PushBreak regularly"]

    return introduction, usability, nudging, effectiveness, integration, acceptance

def print_category(data, category):
    for question in category:
        if question in data:
            print(f"{question}: {data[question]}")
            print(f"Data type: {type(data[question])}, Array dtype: {data[question].dtype}")
            print()

def handle_introduction(data, introduction):
    print(data[introduction[1]])  # Example printing ages
    mean = np.mean(data[introduction[1]]) # Example for mean age
    return mean

def main():
    data = import_data()
    introduction, usability, nudging, effectiveness, integration, acceptance = make_categories()

    print(handle_introduction(data, introduction))

if __name__ == "__main__":
    main()