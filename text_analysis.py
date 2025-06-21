import difflib
import pandas as pd
import numpy as np

def count_correct_characters(reference, user_input):
    """Count the number of correctly typed characters using sequence matching"""
    matcher = difflib.SequenceMatcher(None, reference, user_input)
    correct = 0
    for opcode in matcher.get_opcodes():
        tag, i1, i2, j1, j2 = opcode
        if tag == 'equal':
            correct += (i2 - i1)
    return correct

def calculate_cpm_per_participant(df):
    """Calculate CPM for each participant across all sessions"""

    # Create a list to store results
    results = []

    # Get unique participants
    participants = df['participant_id'].unique()

    for participant in participants:
        # Filter data for this participant
        participant_data = df[df['participant_id'] == participant]

        # Get unique sessions for this participant
        sessions = sorted(participant_data['session_number'].unique())

        # Create a row for this participant
        participant_row = {'participant_id': participant}

        for session in sessions:
            # Get data for this specific session
            session_data = participant_data[participant_data['session_number'] == session]

            # Calculate total correct characters for this session
            total_correct_chars = 0

            for _, row in session_data.iterrows():
                correct_chars = count_correct_characters(row['expected_text'], row['typed_text'])
                total_correct_chars += correct_chars

            # Calculate CPM (characters per minute) - assuming 2 minutes per session
            cpm = total_correct_chars / 2

            # Add to participant row
            participant_row[f'session_{session}_cpm'] = cpm

        results.append(participant_row)

    return pd.DataFrame(results)

def main():
    df = pd.read_csv('csv/typing_texts.csv')

    print(f"Loaded {len(df)} rows of data")
    print(f"Participants: {df['participant_id'].nunique()}")
    print(f"Sessions: {sorted(df['session_number'].unique())}")

    # Calculate CPM for each participant
    print("Calculating CPM for each participant...")
    cpm_df = calculate_cpm_per_participant(df)

    # Display results
    print("\nCPM Results:")
    print(cpm_df)

    # Save to CSV
    output_filename = 'csv/participant_cpm_results.csv'
    cpm_df.to_csv(output_filename, index=False)
    print(f"\nResults saved to: {output_filename}")

    # Optional: Display summary statistics
    print("\nSummary Statistics:")
    session_columns = [col for col in cpm_df.columns if col.startswith('session_')]
    for col in session_columns:
        if col in cpm_df.columns:
            mean_cpm = cpm_df[col].mean()
            std_cpm = cpm_df[col].std()
            print(f"{col}: Mean = {mean_cpm:.2f}, Std = {std_cpm:.2f}")

if __name__ == "__main__":
    main()