import pandas as pd
from io import StringIO
import argparse

def split_table_to_files(input_file, output_directory):
    # Read the table data from the file
    with open(input_file, "r") as file:
        table_data = file.read()

    # Convert the tab-separated data to a Pandas DataFrame
    data = StringIO(table_data)
    df = pd.read_csv(data, sep="\t")

    # Ensure the output directory exists and ends with a slash
    if not output_directory.endswith('/'):
        output_directory += '/'

    # Iterate through the columns and save each as a separate text file
    for column in df.columns[1:]:
        single_col_df = df[['Taxa', column]]

        # Save the DataFrame as a tab-separated text file
        single_col_df.to_csv(f"{output_directory}{column}.txt", index=False, sep="\t")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a table into separate text files based on columns.")
    
    parser.add_argument('-input', required=True, help='Path to the input table file.')
    parser.add_argument('-output', required=True, help='Directory where the output text files will be saved.')

    args = parser.parse_args()

    split_table_to_files(args.input, args.output)
