import os
import pandas as pd
import argparse
import re
import numpy

def vcf_to_hmp(vcf_path, output_path):
    # Read the VCF file
    df = pd.read_csv(vcf_path, sep="\t", comment="#", header=None)
    
    # Extract samples from the VCF header
    with open(vcf_path, 'r') as f:
        for line in f:
            if line.startswith("#CHROM"):
                vcf_samples = line.strip().split("\t")[9:]
                break

    # Rename columns to match VCF format
    df.columns = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"] + vcf_samples
    
    # Convert genotypic information to the desired format for each sample
    for sample in df.columns[9:]:
        df[sample] = df[sample].str.split(":").str[0]
        df[sample] = df.apply(lambda row: row[sample].replace("0/0", row["REF"] + "/" + row["REF"])
                                    .replace("0/1", row["REF"] + "/" + row["ALT"])
                                    .replace("1/1", row["ALT"] + "/" + row["ALT"])
                                    .replace("./.", "N/N"), axis=1)


    # Assign the INFO column
    block_number = os.path.basename(vcf_path).split("_")[1].split(".")[0]
    df["INFO"] = "exonic :: candidate_block" + block_number

    # Calculate the Minor Allele Frequency (assuming 0/1 is heterozygous)
    # Convert the necessary DataFrame columns to numpy arrays
    samples_data = df[df.columns[9:]].to_numpy()
    ref_pattern_array = (df["REF"] + "/" + df["REF"]).to_numpy()[:, None]
    alt_pattern_array = (df["ALT"] + "/" + df["ALT"]).to_numpy()[:, None]
    hetero_pattern_array = (df["REF"] + "/" + df["ALT"]).to_numpy()[:, None]

    # Use broadcasting to calculate counts
    ref_counts = (samples_data == ref_pattern_array).sum(axis=1) + 0.5 * (samples_data == hetero_pattern_array).sum(axis=1)
    alt_counts = (samples_data == alt_pattern_array).sum(axis=1) + 0.5 * (samples_data == hetero_pattern_array).sum(axis=1)

    df["Minor Allele Frequency"] = pd.concat([pd.Series(ref_counts), pd.Series(alt_counts)], axis=1).min(axis=1) / (2 * len(df.columns[9:]))


    # Select the desired columns
    df = df[["#CHROM", "POS", "REF", "ALT", "INFO", "Minor Allele Frequency"] + vcf_samples]

    # Save to output path
    df.to_csv(output_path, sep="\t", index=False)

def process_all_vcfs_in_directory(directory, output_directory):
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get a list of all VCF files in the directory
    vcf_files = [f for f in os.listdir(directory) if re.match(r'block_\d+\.vcf', f)]

    total_files = len(vcf_files)
    print(f"Found {total_files} VCF files to process.")

    # Execute the script for each VCF file
    for idx, vcf_file in enumerate(vcf_files, 1):
        print(f"Processing file {idx}/{total_files}: {vcf_file}")
        
        input_path = os.path.join(directory, vcf_file)
        output_path = os.path.join(output_directory, vcf_file.replace(".vcf", ".hmp.txt"))
        vcf_to_hmp(input_path, output_path)

    print("All files processed successfully.")

def combine_hmp_files(directory, output_file):
    # List all the .hmp.txt files in the directory
    hmp_files = [f for f in os.listdir(directory) if f.endswith('.hmp.txt')]
    
    # Read each file and append to a list of dataframes
    dfs = [pd.read_csv(os.path.join(directory, hmp_file), sep="\t") for hmp_file in hmp_files]
    
    # Concatenate all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Save the combined dataframe to output_file
    combined_df.to_csv(output_file, sep="\t", index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert VCFs to HMP format in a directory and/or combine all HMP files.")
    parser.add_argument('-dir', help='Directory containing the VCF files or .hmp.txt files.')
    parser.add_argument('-output', help='Directory where the HMP files should be saved or path to save the combined file.')
    parser.add_argument('--combine', action='store_true', help='Set this flag to combine all .hmp.txt files instead of processing VCFs.')
    
    args = parser.parse_args()

    if args.combine:
        combine_hmp_files(args.dir, args.output)
    else:
        process_all_vcfs_in_directory(args.dir, args.output)