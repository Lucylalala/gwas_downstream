# load python package
import os
import shutil
import glob
import pandas as pd
import numpy as np
import string
import sys
import csv


# 定义读取非隐藏文件函数listdir_nohidden
# 读取全部文件os.listdir(current_path)
# 定义染色体变换函数 replace_chr
def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))

def replace_chr(tab):
    chrn = []
    for i in range(1,22,1):
        chrn.append(i)
    chr1 = ["1A","2A","3A","4A","5A","6A","7A","1B","2B","3B","4B","5B","6B","7B","1D","2D","3D","4D","5D","6D","7D"]
    return tab['Chr'].replace(chrn,chr1,inplace = True)

#定义一个注释class
class InfoCell(object):


    def __init__(self, chrom, start, end, geneid, genename):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.geneid = geneid
        self.genename = genename

if __name__ == "__main__":
    with open('wheatgeneanno.csv', 'r') as f:
        c2 = f.readlines()

    infoList = []
    for l in range(1, len(c2)):
        c2[l] = c2[l].rstrip('\r\n')
        s= c2[l].split(',')
        chrom = s[0]
        start = int(s[3])
        end = int(s[4])
        geneid = s[8]
        genename = s[9]
        infocell = InfoCell(chrom, start, end, geneid, genename)
        infoList.append(infocell)

#定义一个注释class
class SNPinfoCell(object):
    
    def __init__(self, Snp, Ref, Alt, Chrom, Pos, Anno):
        self.Snp = Snp
        self.Ref = Ref
        self.Alt = Alt
        self.Chrom = Chrom
        self.Pos = Pos
        self.Anno = Anno
if __name__ == "__main__":
    with open('660k_anno.csv', 'r') as f:
        c3 = f.readlines()
        
    infosnp = []
    for l in range(1, len(c3)):
        c3[l] = c3[l].rstrip('\r\n')
        s= c3[l].split(',')
        Snp = s[0]
        Ref = s[1]
        Alt = s[2]
        Chrom = s[3]
        Pos = s[4]
        Anno = s[5]
        snpinfocell = SNPinfoCell(Snp, Ref, Alt, Chrom, Pos, Anno)
        infosnp.append(snpinfocell)   


#current_path = os.getcwd()
path1 = sys.argv[1]
current_path = path1 +'/'

print('current directory:' + current_path )

#获取当前文件夹下的文件

filename_list = listdir_nohidden(current_path)
print('file in current directory:', len(filename_list))

print('going to organize file......')

# 提取结果中小于1e-4的位点

for dirpath, dirnames, filenames in os.walk(current_path):
    for filename in filenames:
        if "GAPIT.Association.GWAS_Results" in filename:
            file_trait = filename.split('.')[-2]
            file_model = filename.split('.')[-3]
            print(os.path.join(dirpath, filename))
            path = os.path.join(dirpath, filename)
            #respath = dirpath + file_model + file_trait + '.csv'
            respath = dirpath + file_trait + '1.csv'

            rescmpath = dirpath + '.' + file_trait + 'cmplot.csv'

            res1 = pd.read_table(path, sep= ',')

            cmplot = pd.read_table(path, sep= ',')

            replace_chr(cmplot)

            cmplot1 = cmplot.iloc[:,0:5]

            cmplot1.to_csv(rescmpath,sep=",",index=None, na_rep = '0', quoting=csv.QUOTE_NONE) 
            
            #res2 = res1[res1["P.value"] <= 1e-4]
            res2 = res1[res1["P.value"] <= 1e-3]

            if res2.shape[0] <= 500:
                res3 = res2.iloc[:,0:5]
            else:
                res3 = res2.iloc[:501,0:5]
            
            res3['trait'] = file_trait
            res3['model'] = file_model

            replace_chr(res3)
            res3.to_csv(respath,sep=",",index=None, na_rep = '0', quoting=csv.QUOTE_NONE) 
            #reanno = dirpath + file_trait + '_anno1.csv'
            reanno = dirpath + file_trait + '_anno1.xlsx'

            res3 = res3.rename(columns={"Pos":"pos","P.value":"pvalue"})

            # 创建一个空的DataFrame用于存储结果
            df = pd.DataFrame(columns=["snp", "chrom", "pos", "pvalue", "snpanno", 
                           "trait", "model", "geneid", "genename", 
                           "start", "end"])

            for index, row in res3.iterrows():
                annex = str(row.SNP)
                Chrom = str(row.Chr)
                POS = int(row.pos)
                pvalue = float(row.pvalue)
                trait = str(row.trait)
                model = str(row.model)

                snpanno = list(filter(lambda x: x.Snp == annex, infosnp))[0].Anno
    
                # 查找满足条件的记录
                res = list(filter(lambda x: x.chrom == Chrom and 
                      x.start - 2000 < POS and 
                      x.end + 2000 > POS,
                      infoList))
    
                if len(res) >= 1:
                    geneid = res[0].geneid
                    genename= res[0].genename
                    start= str(res[0].start)
                    end= str(res[0].end)        
                else:
                    geneid, genename, start, end ='undefined', 'undefined', 'undefined', 'undefined'
    
                # 将结果添加到df中
                df.loc[index] =[annex, Chrom,str(POS),str(pvalue),
                    str(snpanno),str(trait),str(model),
                    geneid, genename,start,end]

            # 将df写入Excel文件
            df.to_excel(reanno,index=False)         

"""
            res3 = res3.rename(columns={"Pos": "pos", "P.value": "pvalue"})
            header = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%("snp", "chrom", "pos","pvalue","snpanno","trait","model","gene","genename","start","end")

            with open(reanno, 'w') as t:
                t.write(header)
                for index, row in res3.iterrows():
                    annex = str(row.SNP)
                    Chrom = str(row.Chr)
                    POS = int(row.pos)
                    pvalue = float(row.pvalue)
                    trait = str(row.trait)
                    model = str(row.model)
                    
                    snpanno = list(filter(lambda x: x.Snp == annex, infosnp))[0].Anno
                   
                    t.write(annex + '\t' + Chrom + '\t' + str(POS) + '\t' + str(pvalue) + '\t' + str(snpanno) + '\t' + str(trait) + '\t' + str(model) + '\t')
                    #finaltext += "%s\t%s\t%s\n"%(snp, Chrom, POS)
                    res = list(filter(lambda x: x.chrom == Chrom and x.start-2000 < POS and x.end+2000 > POS, infoList))
                    if (len(res) >= 1):
                        t.write(res[0].geneid + '\t' + res[0].genename + '\t' + str(res[0].start) + '\t' + str(res[0].end) + '\n')
                    else:
                        t.write('undefined' + '\n')
            t.close()
"""
