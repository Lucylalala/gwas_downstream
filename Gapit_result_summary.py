
import os
import shutil
import glob
import pandas as pd
import numpy as np
import string
import sys
import csv
import re
import argparse

# Define the function to list non-hidden files
def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

# Define chromosome conversion functions
def replace_chr(tab):
    chrn = [i for i in range(1, 22)]
    chr1 = ["1A", "2A", "3A", "4A", "5A", "6A", "7A", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "1D", "2D", "3D", "4D", "5D", "6D", "7D"]
    tab['Chromosome'].replace(chrn, chr1, inplace=True)

def replace_chrd(tab):
    chrABC = ["1A", "2A", "3A", "4A", "5A", "6A", "7A", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "1D", "2D", "3D", "4D", "5D", "6D", "7D"]
    chrdigit = [i for i in range(1, 22)]
    tab['Chromosome'].replace(chrABC, chrdigit, inplace=True)

def get_chrd(chromosome):
    chrn1 = [str(i) for i in range(1, 22)]
    chrd1 = ["1A", "2A", "3A", "4A", "5A", "6A", "7A", "1B", "2B", "3B", "4B", "5B", "6B", "7B", "1D", "2D", "3D", "4D", "5D", "6D", "7D"]
    chrdict1 = dict(zip(chrd1, chrn1))
    return chrdict1[chromosome]

def main(input_dir):
    current_path = input_dir
    print('current directory:' + current_path)

    filename_list = listdir_nohidden(current_path)
    print('file in current directory:', len(filename_list))

    print('going to organize file......')

    dir1stl = glob.glob(current_path + '*')
    print(dir1stl)

    root_dir = input_dir

    final_df = pd.DataFrame()
    for trait_dir in glob.glob(root_dir + "*/"):
        print(trait_dir)
        anno1lst = glob.glob(trait_dir + '*anno1.xlsx')
        if not anno1lst: 
            continue
        print(trait_dir)
        anno_alllst = []
        for anno_file in anno1lst:
            anno1 = pd.read_excel(anno_file)
            anno_alllst.append(anno1)
        anno_all = pd.concat(anno_alllst)
        print(anno_all.shape)
        anno_all_f = anno_all.drop_duplicates(subset=['snp'], keep='first', inplace=False, ignore_index=True)
        print(anno_all_f.shape)
        filename = os.path.basename(os.path.normpath(trait_dir))
        anno_all['subdirectory'] = filename
        filename = os.path.basename(os.path.normpath(trait_dir))
        anno_all.to_excel(trait_dir + filename + "_summarize.xlsx", index=None, na_rep='0')
        final_df = pd.concat([final_df, anno_all])

    final_df.to_excel(os.path.join(root_dir, "final_summarize.xlsx"), index=None, na_rep='0')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze data in a specific path.')
    parser.add_argument('-input', type=str, required=True, help='Path to analyze')
    args = parser.parse_args()
    
    main(args.input)
