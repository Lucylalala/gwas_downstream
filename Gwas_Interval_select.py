# lushan
import pandas as pd
import subprocess
import os
import time
from multiprocessing import Pool
import argparse


def convert_chrd_name(chrom_name):
    chrABC = ["1A","2A","3A","4A","5A","6A","7A","1B","2B","3B","4B","5B","6B","7B","1D","2D","3D","4D","5D","6D","7D"]
    chrdigit = [str(i) for i in range(1, 22)]
    conversion_dict = dict(zip(chrABC, chrdigit))
    return conversion_dict.get(chrom_name, chrom_name)

def run_ldblockshow(args):
    chrom, interval_start, interval_end, region_counter, vcf_path, significant_snps = args
    dir_name = f"{chrom}_{interval_start}_{interval_end}"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Convert chromosome name for LDBlockShow
    converted_chrom = convert_chrd_name(chrom)

    # Run LDBlockShow for the interval
    cmd = f"LDBlockShow -InVCF {vcf_path} -OutPng -BlockType 3 -BlockCut 0.85:0.90 -SeleVar 2 -Region {converted_chrom}:{interval_start}:{interval_end} -OutPut {dir_name}/region{region_counter} -NoShowLDist 5000000"
    subprocess.run(cmd, shell=True)

    # Export the table for the interval to the same directory
    interval_data = significant_snps[(significant_snps['chrom'] == chrom) & 
                                     (significant_snps['pos'] >= interval_start) & 
                                     (significant_snps['pos'] <= interval_end)]

    interval_data.to_excel(f"{dir_name}/{chrom}_{interval_start}_{interval_end}.xlsx", index=False)

def main():
    # Start the timer
    start_time = time.time()
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Process command-line arguments.")
    parser.add_argument('-vcf', required=True, help='Path to the VCF file.')
    parser.add_argument('-summary', required=True, help='Path to the summary Excel file.')
    parser.add_argument('-processes', type=int, default=4, help='Number of processes to use. Default is 4.')
    
    args = parser.parse_args()

    # Assigning paths from command-line arguments
    vcf_path = args.vcf
    summary_path = args.summary
    num_processes = args.processes
    
    # Step 1: Read the Excel file using summary_path
    data = pd.read_excel(summary_path)


    # Step 2: Filter out significant SNPs
    significant_snps = data[data['pvalue'] < 1e-3]

    # Step 3: Generate fixed intervals across the genome based on sub-genome lengths
    intervals_list = []

    subgenome_lengths = {
    'A': 1520000,
    'B': 3325000,
    'D': 1660000
    }

    for chrom in significant_snps['chrom'].unique():
        subgenome = chrom[-1]  # Extracting sub-genome letter from chromosome name
        interval_length = subgenome_lengths[subgenome]
    
        min_pos = significant_snps[significant_snps['chrom'] == chrom]['pos'].min()
        max_pos = significant_snps[significant_snps['chrom'] == chrom]['pos'].max()
    
        for start_pos in range(min_pos, max_pos, interval_length):
            end_pos = start_pos + interval_length
            intervals_list.append((chrom, start_pos, end_pos))

    fixed_intervals_df = pd.DataFrame(intervals_list, columns=['chrom', 'interval_start', 'interval_end'])

    # Step 4: Aggregate SNPs and environments for each interval
    def aggregate_snps(row):
        return significant_snps[(significant_snps['chrom'] == row['chrom']) & 
                            (significant_snps['pos'] >= row['interval_start']) & 
                            (significant_snps['pos'] <= row['interval_end'])]['snp'].unique()

    def aggregate_environments(row):
        return significant_snps[(significant_snps['chrom'] == row['chrom']) & 
                            (significant_snps['pos'] >= row['interval_start']) & 
                            (significant_snps['pos'] <= row['interval_end'])]['subdirectory'].unique()

    fixed_intervals_df['unique_snps'] = fixed_intervals_df.apply(aggregate_snps, axis=1)
    fixed_intervals_df['unique_environments'] = fixed_intervals_df.apply(aggregate_environments, axis=1)

    fixed_intervals_df['unique_snps_count'] = fixed_intervals_df['unique_snps'].apply(len)
    fixed_intervals_df['unique_environments_count'] = fixed_intervals_df['unique_environments'].apply(len)

    # Step 5: Filter intervals with two or more unique SNPs
    filtered_fixed_intervals = fixed_intervals_df[fixed_intervals_df['unique_snps_count'] >= 2]



    # Create a list of arguments to feed into the function
    args_list = [(row.chrom, row.interval_start, row.interval_end, index, vcf_path, significant_snps) for index, row in enumerate(filtered_fixed_intervals.itertuples(), 1)]


    # Use a Pool to run subprocesses in parallel
    with Pool(processes=num_processes) as pool:
        pool.map(run_ldblockshow, args_list)

    # Export summary table
    filtered_fixed_intervals.to_excel("intervals_summary.xlsx", index=False)

    # End the timer and print the time taken
    end_time = time.time()
    print(f"Time taken to run the script: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    main()
