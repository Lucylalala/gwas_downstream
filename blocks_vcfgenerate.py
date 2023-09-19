import pandas as pd
import argparse
import os
from multiprocessing import Pool

def replace_chrd(tab):
    chrABC = ["1A", "2A", "3A", "4A", "5A", "6A", "7A", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "1D", "2D", "3D", "4D", "5D", "6D", "7D"]
    chrdigit = list(range(1, 22))
    tab['chr'].replace(chrABC, chrdigit, inplace=True)
    return tab

def process_block(args):
    vcf_lines, header_line, row, index, block_output_dir = args
    chr_name = str(row['chr'])
    start = row['start']
    end = row['end']
    
    print(f"Checking block: {chr_name}:{start}-{end}")

    block_snps = [line for line in vcf_lines if not line.startswith("#") and line.split("\t")[0] == chr_name and start <= int(line.split("\t")[1]) <= end]
    print(f"Number of SNPs in block: {len(block_snps)}")
    
    block_output_path = os.path.join(block_output_dir, f"block_{index + 1}.vcf")
    with open(block_output_path, 'w') as f:
        f.write(header_line)  # write the header line
        f.writelines(block_snps)

    return block_snps

def filter_vcf_by_blocks(vcf_path, block_details_path, final_output_path, block_output_dir, processes):
    if not os.path.exists(block_output_dir):
        os.makedirs(block_output_dir)

    block_details = pd.read_excel(block_details_path)
    replace_chrd(block_details)

    with open(vcf_path, 'r') as f:
        vcf_lines = f.readlines()
        header_line = [line for line in vcf_lines if line.startswith("#CHROM")][0]  # extract the header line

    print(f"Total number of blocks: {len(block_details)}")
    print(f"Total number of SNPs in VCF: {len(vcf_lines) - 1}")  # subtracting the header line

    block_args = [(vcf_lines, header_line, row, index, block_output_dir) for index, row in block_details.iterrows()]

    with Pool(processes=processes) as pool:
        results = pool.map(process_block, block_args)

    filtered_snps = [header_line] + [snp for block in results for snp in block]

    with open(final_output_path, 'w') as f:
        f.writelines(filtered_snps)

    print(f"Filtered VCF saved to: {final_output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter a VCF file based on block details.")
    parser.add_argument('-vcf', required=True, help='Path to the input VCF file.')
    parser.add_argument('-blocks', required=True, help='Path to the Excel file containing block details.')
    parser.add_argument('-output', required=True, help='Path where the final filtered VCF should be saved.')
    parser.add_argument('-block_output_dir', required=True, help='Directory where individual block VCFs will be saved.')
    parser.add_argument('-processes', type=int, default=4, help='Number of processes to use for parallel processing.')

    args = parser.parse_args()
    filter_vcf_by_blocks(args.vcf, args.blocks, args.output, args.block_output_dir, args.processes)
