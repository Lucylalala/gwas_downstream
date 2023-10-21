import os
import shutil
import glob
import sys 

import os
import shutil
import glob
import sys

# 定义读取非隐藏文件函数listdir_nohidden
# 读取全部文件os.listdir(current_path)
def listdir_nohidden(path):
    return glob.glob(os.path.join(path, '*'))


#current_path = os.getcwd()
path1 = sys.argv[1]
current_path = path1 +'/'

print('current directory:' + current_path )

#获取当前文件夹下的文件

filename_list = listdir_nohidden(current_path)
print('file in current directory:', len(filename_list))

print('going to organize file......')

# 根据性状分类
for i in range(len(filename_list)):
    filename = filename_list[i]
    file_trait = filename.split('.')[-2]
    try:
        os.mkdir(current_path + file_trait)
        print('create dir' + file_trait)
    except:
        pass
    try:
        shutil.move(filename,current_path+'/'+file_trait)
        print(filename+'move success')
    except Exception as e:
        print('move failed')

print("All files have moved")


# 根据模型分类
traitdir = []
# 遍历文件夹下所有子文件并保存到list里
for dirpath, dirnames, filenames in os.walk(current_path):
    for dirname in dirnames:
        m = os.path.join(dirpath, dirname)
        traitdir.append(m)
print(traitdir)

for i in range(len(traitdir)):
    c_path = traitdir[i]
    print('current directory:' + c_path )
    filelist = listdir_nohidden(c_path)
    print('going to organize file......')
    
    for i in range(len(filelist)):
        fame = filelist[i]
        file_model = fame.split('.')[3]
        try:
            os.mkdir(c_path + '/' + file_model)
            print('create dir' + file_model)
        except:
            pass
        try:
            shutil.move(fame,c_path + '/' + file_model)
            print(fame + 'move success')
        except Exception as e:
            print(fame + 'move failed')

print("All files have moved")
