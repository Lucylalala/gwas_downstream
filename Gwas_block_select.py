import pandas as pd
import os
import gzip
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Process command-line arguments.")
parser.add_argument('-input', required=True, help='Path to the directory containing all interval directories.')
args = parser.parse_args()

# Check if the provided directory exists
if not os.path.exists(args.input):
    print(f"Error: The directory '{args.input}' does not exist.")
    exit(1)

# Set the path to the directory containing all interval directories
base_path = args.input
# Global list to store all blocks' details
all_blocks_details = []

# Chromosome transformation function
def replace_chr(tab):
    chrn = list(range(1, 22))
    chr1 = ["1A","2A","3A","4A","5A","6A","7A","1B","2B","3B","4B","5B","6B","7B","1D","2D","3D","4D","5D","6D","7D"]
    tab['chr'].replace(chrn, chr1, inplace=True)

def process_interval(interval_dir):
    # Check if the Excel file with significant SNPs exists in the directory
    excel_file_name = os.path.basename(interval_dir) + ".xlsx"
    excel_file = os.path.join(interval_dir, excel_file_name)
    
    if not os.path.exists(excel_file):
        print(f"Excel file for {interval_dir} not found. Skipping this directory.")
        return None

    # Read the significant SNPs
    significant_snps = pd.read_excel(excel_file)

    # Dynamically find the block file in the directory
    block_files = [f for f in os.listdir(interval_dir) if f.endswith(".blocks.gz")]
    if not block_files:
        print(f"Block file for {interval_dir} not found. Skipping this directory.")
        return None
    block_file = os.path.join(interval_dir, block_files[0])

    try:
        with gzip.open(block_file, 'rt') as f:
            block_data = pd.read_csv(f, sep="\t", skiprows=1, header=None)
    except pd.errors.EmptyDataError:
        print(f"Block file for {interval_dir} is empty or has invalid data. Skipping this directory.")
        return None

    # Assign column names
    block_data.columns = ['chr', 'start', 'end', 'SNPNumber', 'TagSNPList']
    replace_chr(block_data)

    # Count how many unique significant SNPs are within a block and unique environments
    def count_unique_significant_snps(row):
        block_start = row['start']
        block_end = row['end']
        unique_snps_within_block = significant_snps[(significant_snps['pos'] >= block_start) & (significant_snps['pos'] <= block_end)]['snp'].unique()
        return len(unique_snps_within_block)

    # Count how many unique environments a block is associated with
    def count_unique_environments(row):
        block_start = row['start']
        block_end = row['end']
        unique_environments = significant_snps[(significant_snps['pos'] >= block_start) & (significant_snps['pos'] <= block_end)]['subdirectory'].unique()
        return len(unique_environments)

    block_data['unique_significant_snps_count'] = block_data.apply(count_unique_significant_snps, axis=1)
    block_data['unique_environments_count'] = block_data.apply(count_unique_environments, axis=1)


    # Filter the blocks that have at least two unique significant SNPs
    candidate_blocks = block_data[block_data['unique_significant_snps_count'] >= 2]

    # Export details of each candidate block and also append block details to the global list
    for index, row in candidate_blocks.iterrows():
        block_data_subset = significant_snps[(significant_snps['pos'] >= row['start']) & (significant_snps['pos'] <= row['end'])]
        
        # Create directory for the block within the interval directory if it doesn't exist
        block_dir_name = f"{interval_dir}/blocks/{row['chr']}_{row['start']}_{row['end']}"
        if not os.path.exists(block_dir_name):
            os.makedirs(block_dir_name)
        
        # Save block data to the block directory
        block_data_subset.to_excel(f"{block_dir_name}/{row['chr']}_{row['start']}_{row['end']}.xlsx", index=False)
        
        # Append block details to the global list
        all_blocks_details.append({**row.to_dict(), **{'block_name': f'candidate_block{len(all_blocks_details) + 1}'}})
        
    # Export summary table for the interval
    candidate_blocks[['chr', 'start', 'end', 'unique_significant_snps_count', 'unique_environments_count']].to_excel(f"{interval_dir}/blocks_summary.xlsx", index=False)

    if not candidate_blocks.empty:
        return interval_dir
    else:
        return None

    

# Get all directories in the base_path directory
all_directories = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
interval_directories = [d for d in all_directories if "_" in d and any(c.isdigit() for c in d)]

intervals_with_candidate_blocks = []
for interval_dir in interval_directories:
    result = process_interval(interval_dir)
    if result:
        intervals_with_candidate_blocks.append(result)

# Save the summary to a table
summary_df = pd.DataFrame({
    'Intervals_with_candidate_blocks': intervals_with_candidate_blocks
})
summary_df.to_excel(f"{base_path}/intervals_summary.xlsx", index=False)

# Convert the list of all blocks' details to a DataFrame and save to an Excel file
all_blocks_df = pd.DataFrame(all_blocks_details)
all_blocks_df.to_excel(f"{base_path}/all_blocks_details.xlsx", index=False)
