import pandas as pd
from collections import defaultdict
import argparse

def parse_text_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = defaultdict(list)
    current_group = 0

    for line in lines:
        line = line.strip()
        if line.startswith("Password Hash:"):
            current_group += 1
        elif line.startswith("-"):
            username = line[2:]  # Remove the leading '- ' from the username
            data[current_group].append(username)

    return data

def write_to_excel(data, output_file):
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        for group_number, usernames in data.items():
            # Create a DataFrame for the current group
            df = pd.DataFrame(usernames, columns=['Usernames'])
            # Create a sequential sheet name
            sheet_name = f"Sheet{group_number}"
            # Write the DataFrame to a sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def main():
    parser = argparse.ArgumentParser(description="Process a text file and export users with the same password to an Excel file with separate sheets.")
    parser.add_argument('input_file', type=str, help='Path to the input text file.')
    parser.add_argument('output_file', type=str, help='Path to the output Excel file.')

    args = parser.parse_args()

    # Parse the text file
    parsed_data = parse_text_file(args.input_file)

    # Write the parsed data to an Excel file
    write_to_excel(parsed_data, args.output_file)

    print(f"Data has been written to {args.output_file}")

if __name__ == "__main__":
    main()
