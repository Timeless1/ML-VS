################################################################
# Prepared by Ma Wei: 2020-05-11                               #
#                                                              #
# Requiremnets:                                                #
# 1 dirs to be checked                                         #
#   ../../single_mol2/    single mol2 files for every molecule #
#   ../rdock              rdock for 2nd docking                #
# 2 resultfiles:                                               #
#  recList.txt_ligList.txt.pdbqt.gz                            #
#                                                              #
# 3 better add a zip process of ./models                       #
#                                                              #
################################################################

import re
import os
import subprocess
import pandas as pd
import time
import logging

start = time.time()

def runcmd(command):
    ret = subprocess.run(command)
    if ret.returncode == 0:
        print("success:", ret)
    else:
        print("error:", ret)
       
def vinalc_split(filename):              
    command = (["mkdir", "../outputfile/models"])
    runcmd(command)
    # Step 1 Extract First Pose
    with open("%s"%filename, "r") as fh:
        allLines = fh.readlines()
        fh.close()
        writeindex = 0
        index = -1
        for line in allLines:
            index += 1
            if re.search("REMARK RECEPTOR", line):
                next_four_line = allLines[index + 4]
                a = next_four_line.split()
                fh2 = open("../outputfile/models/%s.pdbqt"%a[3], "w")
                if writeindex == 0:
                    writeindex = 1
                else:
                    pass
            if writeindex == 1:
                fh2.write(line)

    # Step 2 Extract docking Score of First Pose
    path = "../outputfile/models"
    filenames = os.listdir(path)
    filenames.sort()
    score_dict = {}
    for i in filenames:
        fh = open("../outputfile/models/%s"%i, 'r')
        alllines = fh.readlines()
        try:
            line = alllines[3]
        except: IndexError
        a = line.split()
        score_dict["%s"%i[:-6]] = float("%s"%a[3])
    #print(score_dict)
    ligand_list = []
    key_value = []
    for j in sorted(score_dict, key=score_dict.__getitem__):
        ligand_list.append(j)
        key_value.append((j, score_dict["%s"%j]))
    #print(ligand_list)
    #print(key_value)
    fh_key_value = open("../outputfile/key_value.txt", "w")
    for l in key_value:
        key = l[0]
        value = l[1]
        fh_key_value.write(key)
        fh_key_value.write('\t')
        fh_key_value.write(str(value))
        fh_key_value.write('\n')
    fh_key_value.close()


def sort_vinalc_result(filename):  
    index = 0
    fh2 = open("%s"%filename, "w")
    for k in ligand_list:
        fh = open("../outputfile/models/%s.pdbqt"%k, 'r')
        alllines = fh.readlines()
        fh.close()
        writeindex = 0
        for line in alllines:
            if re.search("MODEL", line):
                if writeindex == 0:
                    writeindex = 1
                else:
                    break
            if writeindex == 1:
                fh2.write(line)
        index += 1
        print("-----------------------No.%s-------------------"%index)
    fh2.close()

    command2 = (["obabel", "-ipdbqt", "%s"%filename, "-omol2", "-O", "final_result.mol2"])
    runcmd(command2)

def extract_top_x(filename):
    ## Step 3 Extract top 20%
    percent = 0.2
    fh = open("%s"%filename, "r")
    allLines = fh.readlines()
    fh.close()
    lines_number = len(allLines)
    top_x = int(lines_number * percent)
    top_x_List = allLines[0:top_x + 1]
    fh2 = open("../outputfile/vinalc_top20.txt", "w+")
    for i in top_x_List:
        fh2.write(i)
    fh2.close()
    
## Step 4 Generate top20% mol2 File for Rdock
def get_mol2(filename1, filename2):
    fh_0 = open("%s"%filename1, "w+")
    fh = open("%s"%filename2, "r")
    alllines = fh.readlines()
    for line in alllines:
        line = line.split()[0]
        try:
            fh3 = open("/home/iip_pkuhpc/iip_test/lustre3/mawei/AI/score-consensus/data/single_mol2_chemDiv/%s.mol2"%line, "r")
        except FileNotFoundError:
            fh3 = open("../active_decoys_single_mol2/%s.mol2"%line, "r")
        fh3_alllines = fh3.readlines()
        fh3.close()
        for line2 in fh3_alllines:
            fh_0.write(line2)   
    fh.close()
    fh_0.close()    
    command2 = (["obabel", "-imol2", "%s"%filename1, "-osd", "-O", "../outputfile/compounds_rdock.sd"])
    runcmd(command2)
    
    ###clear
    command3 = (["7z", "a", "../outputfile/models.7z", "../outputfile/models"])
    runcmd(command3)
    command4 = (["rm", "-rf", "../outputfile/models"])
    runcmd(command4)



##########################################
##        get model_train_dataset       ##
##########################################

#model_1
def label_model_1(x):
    if float(x[:-1]) <= 20:
        return 1
    elif float(x[:-1]) > 80:
        return 0
        
#model_2
def label_model_2(x):
    if float(x[:-1]) <= 20:
        return 1
    elif float(x[:-1]) > 60:
        return 0  
        
#model_3        
def label_model_3(x):
    if float(x[:-1]) <= 20:
        return 1
    elif float(x[:-1]) > 20:
        return 0    

def get_model_train_data(number): 
    score_data = open("../outputfile/vinalc_top20.txt", "r")
    res = []
    for i in score_data:
        d = [x for x in i.strip().split()]
        res.append(d)
    save = pd.DataFrame(columns=['UniqueID', 'vinalc_score'], index=None, data=res) 
    score_data.close()
    top_x_list = []  
    for i in range(1, len(save) + 1):
        top_x_list.append("%.2f%%" % (i/len(save) * 100))   
    save["top_x"] = top_x_list
    values = save['top_x'].apply(lambda x: number(x))  
    save['label'] = values
    label_data = save.loc[save['label'].isin(['0', '1'])]
    smiles_data = pd.read_csv("../inputfile/smiles_all.csv")
    label_data = pd.merge(label_data, smiles_data, how="inner", left_on="UniqueID", 
                          right_on="UniqueID")
    bool_active_decoys = label_data['UniqueID'].str.contains('active|decoy')
    bool_ligand = label_data['UniqueID'].str.contains('ligand')
    active_decoys_data = label_data[bool_active_decoys]
    active_decoys_data.rename(columns={'label':'true_label'}, inplace=True)
    train_data = label_data[bool_ligand]
    return train_data, active_decoys_data
 

if __name__ == '__main__':
    vinalc_split("recList.txt_ligList.txt.pdbqt.gz")
    extract_top_x("../outputfile/key_value.txt")
    get_mol2("../outputfile/vinalc_top_20.mol2", "../outputfile/vinalc_top20.txt")

    train_data, active_decoys_data = get_model_train_data(label_model_1)
    train_data.to_csv("../outputfile/vinalc_model_1_train.csv", index=False)
    active_decoys_data.to_csv("../outputfile/vinalc_model_1_active_decoys.csv", index=False)

    train_data, active_decoys_data = get_model_train_data(label_model_2)
    train_data.to_csv("../outputfile/vinalc_model_2_train.csv", index=False)
    active_decoys_data.to_csv("../outputfile/vinalc_model_2_active_decoys.csv", index=False)

    train_data, active_decoys_data = get_model_train_data(label_model_3)
    train_data.to_csv("../outputfile/vinalc_model_3_train.csv", index=False)
    active_decoys_data.to_csv("../outputfile/vinalc_model_3_active_decoys.csv", index=False)

########################################################################
#                                                                      #
#                                                                      #
#   #######              #######       #####        ######    #     #  # 
#   #      #            #       #   #       #    #           #   #     # 
#   ######     #####   #       #   #       #    #           ##         #       
#   #     #           #       #   #       #    #           #   #       #    
#   #       #        #######       #####        ######    #      #     #
#                                                                      #
#                                                                      #
########################################################################

    ##run-rdock
    command = (["./rdock.sh"])
    runcmd(command)
    print("sbatch rdock passing")
    
    end = time.time()
    cost = end - start
    print("Time cost for sort for vinalc:", "%s seconds"%cost)
    logging.basicConfig(filename='../outputfile/time-cost-vinalc-process.log', level=logging.INFO)
    logging.info("Time cost for sort for vinalc:%s seconds"%cost)
