import pandas as pd
import argparse

def replace_chrd(tab):
    """
    Function to replace chromosome names with numbers.
    """
    chrABC = ["1A","2A","3A","4A","5A","6A","7A","1B","2B","3B","4B","5B","6B","7B","1D","2D","3D","4D","5D","6D","7D"]
    chrdigit = list(range(1, 22))
    tab['chr'].replace(chrABC, chrdigit, inplace=True)
    return tab

def generate_gff_from_blocks(input_path, output_path):
    # Load the all_blocks_details data
    all_blocks_details_df = pd.read_excel(input_path)
    all_blocks_details_df = replace_chrd(all_blocks_details_df)

    # Prepare the GFF output
    gff_output = []

    for index, row in all_blocks_details_df.iterrows():
        block_id = row['block_name']
        chr_name = row['chr']
        block_start = row['start']
        block_end = row['end']

        # Gene entry
        gene_entry = [f"{chr_name}", "IWGSC", "gene", f"{block_start}", f"{block_end}", ".", "-", ".", f"ID=gene:{block_id};biotype=protein_coding;"]
        gff_output.append(gene_entry)

        # mRNA entry
        mRNA_entry = [f"{chr_name}", "IWGSC", "mRNA", f"{block_start}", f"{block_end}", ".", "-", ".", f"ID=transcript:{block_id}.1;Parent=gene:{block_id};"]
        gff_output.append(mRNA_entry)

        # Exon entry
        exon_entry = [f"{chr_name}", "IWGSC", "exon", f"{block_start}", f"{block_end}", ".", "-", ".", f"Parent=transcript:{block_id}.1;"]
        gff_output.append(exon_entry)

        # CDS entry
        CDS_entry = [f"{chr_name}", "IWGSC", "CDS", f"{block_start}", f"{block_end}", ".", "-", "0", f"ID=CDS:{block_id}.1.cds1;Parent=transcript:{block_id}.1;"]
        gff_output.append(CDS_entry)

    # Convert the GFF output to DataFrame
    gff_df = pd.DataFrame(gff_output)

    # Save the GFF output to a file
    gff_df.to_csv(output_path, sep="\t", index=False, header=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate GFF file from block details.")
    parser.add_argument('-input', required=True, help='Path to the all_blocks_details.xlsx file.')
    parser.add_argument('-export', required=True, help='Path where the GFF file should be saved.')
    
    args = parser.parse_args()
    
    generate_gff_from_blocks(args.input, args.export)

