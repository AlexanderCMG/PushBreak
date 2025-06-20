import pandas as pd


def import_data():
    # === Step 1: Load the CSV ===
    file_path = "PushBreak_June+20,+2025_01.58.csv"
    df_raw = pd.read_csv(file_path)

    # === Step 2: Extract question labels (row 0) ===
    question_labels = df_raw.iloc[0]

    # === Step 3: Extract response data (from row 2 onwards) ===
    df_responses = df_raw.iloc[2:].reset_index(drop=True)
    df_responses.columns = question_labels

    # === Step 4: Drop metadata columns (optional) ===
    df_responses = df_responses.loc[:, ~df_responses.columns.str.contains(
        'Unnamed|Response ID|Recipient|Start Date|End Date|Response Type|Progress|Duration|Finished|Recorded|Location|UserLanguage|IP Address|External Data Reference|Distribution Channel|User Language|Do you agree to the details set out in the consent form?',
        case=False
    )]

    # === Step 5: Create dictionary: {question text: [responses]} ===
    question_data = {
        question: df_responses[question].tolist()
        for question in df_responses.columns
    }

    # === Done! You can now use `question_data` in your analysis ===
    for key, value in question_data.items():
        print(f"{key}: {value}")

    return question_data

def make_categories():
    introduction = ["Participant number", "What is your age?", "What is your gender?", "How many hours a day do you normally spend sitting? - Hours", "Have you ever used a footrest while working or studying?", "Have you used any time management apps or timers to remind you to take breaks?", "Do you have any experience using the Pomodoro technique for working or studying?"]
    usability = ["I found PushBreak easy to use", "I felt confident using PushBreak", "I found PushBreak unnecessarily complex", "I think most people would learn to use PushBreak very quickly", "I needed to learn a lot of things before I could get going with PushBreak"]
    nudging = ["I noticed when the nudging from PushBreak started", "I felt the urge to move or get up at the right time", "The nudging of the device was…", "The shape-changing feedback clearly signalled that it was time to take a break", "The timing of the nudges was appropriate for my workflow"]
    effectiveness = ["PushBreak helped me become more aware of how long I had been sitting", "PushBreak encouraged me to take breaks", "I would be more likely to take micro-breaks if I used PushBreak regularly", "I felt that PushBreak successfully changed my behaviour", "I felt that PushBreak was more effective than a timer"]
    integration = ["PushBreak felt like a natural part of my workspace", "PushBreak supported my workflow rather than interrupting it", "PushBreak’s physical presence and feedback were well integrated into the environment"]
    acceptance = ["I would consider using a similar device in my workspace", "I would choose PushBreak over a conventional timer", "Using PushBreak made me feel more responsible about my health", "I would like to use PushBreak regularly"]

    return introduction, usability, nudging, effectiveness, integration, acceptance

def print_category(data, category):
    for question in category:
        print(data[question])

def main():
    data = import_data()
    introduction, usability, nudging, effectiveness, integration, acceptance = make_categories()

    print_category(data, introduction)
    print_category(data, usability)
    print_category(data, nudging)
    print_category(data, effectiveness)
    print_category(data, acceptance)

main()


