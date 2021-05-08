#!/usr/bin/python3
# coding:utf-8
# Author:weima
# title:get_label.py
# description: get data label for database
# date:20200509
# usage:python get_label.py

import pandas as pd
import subprocess
import time
import logging
start = time.time()

##model_1
def label_model_1(x):
    if float(x[:-1]) <= 20:
        return 1
    elif float(x[:-1]) > 80:
        return 0

##model_2
def label_model_2(x):
    if float(x[:-1]) <= 20:
        return 1
    elif float(x[:-1]) > 60:
        return 0

##model_3
def label_model_3(x):
    if float(x[:-1]) <= 20:
        return 1
    elif float(x[:-1]) > 20:
        return 0
#get train_data for model
def get_database():
    fh1 = open("../outputfile/result_all.sd", "w")
    for i in range(1, 31):
        fh2 = open("../outputfile/result_%s.sd"%i, "r")
        alllines = fh2.readlines()
        fh2.close()
        for line in alllines:
            fh1.write(line)
    fh1.close()

    process = subprocess.Popen('sdreport -c ../outputfile/result_all.sd > ../outputfile/rdock_result.csv', shell=True)
    process.wait()
    df = pd.DataFrame(pd.read_csv("../outputfile/rdock_result.csv"))
    df.rename(columns={'_TITLE1':'UniqueID', 'INTER':'rdock_score'}, inplace=True)
    df2 = df.sort_values(by="rdock_score", ascending=True)
    df3 = df2.drop_duplicates(['UniqueID'])
    df3['rank'] = range(1, len(df3) + 1)

    top_x_list = []
    for i in range(1, len(df3) + 1):
        top_x_list.append("%.2f%%" % (i/len(df3) * 100))
    df3["top_x"] = top_x_list
    #merge
    df4 = pd.DataFrame(pd.read_csv('../inputfile/smiles_all.csv'))
    df_merge = pd.merge(df3, df4, how="inner", left_on="UniqueID", right_on="UniqueID")
    df_merge.to_csv("../outputfile/database.csv", sep=",", header=True, index=False)

##get_model_train_data
def get_model_train_data(number):
    data_df = pd.read_csv("../outputfile/database.csv")
    data_part = data_df[['UniqueID', 'smiles', 'rdock_score', 'rank', 'top_x']]
    values = data_part['top_x'].apply(lambda x: number(x))
    data_part['label'] = values
    #get data of label 0 & 1
    label_data = data_part.loc[data_part['label'].isin(['0', '1'])]
    #split traindataset & active/decoys
    bool_active_decoys = label_data['UniqueID'].str.contains('active|decoy')
    bool_ligand = label_data['UniqueID'].str.contains('ligand')
    active_decoys_data = label_data[bool_active_decoys]
    active_decoys_data.rename(columns={'label':'true_label'}, inplace=True)
    train_data = label_data[bool_ligand]
    return train_data, active_decoys_data


if __name__ == '__main__':
    get_database()
    ###get double_dock traindataset for 3 models
    train_data, active_decoys_data = get_model_train_data(label_model_1)
    train_data.to_csv("../outputfile/double_dock_model_1_train.csv", index=False)
    active_decoys_data.to_csv("../outputfile/double_dock_model_1_active_decoys.csv", index=False)

    train_data, active_decoys_data = get_model_train_data(label_model_2)
    train_data.to_csv("../outputfile/double_dock_model_2_train.csv", index=False)
    active_decoys_data.to_csv("../outputfile/double_dock_model_2_active_decoys.csv", index=False)

    train_data, active_decoys_data = get_model_train_data(label_model_3)
    train_data.to_csv("../outputfile/double_dock_model_3_train.csv", index=False)
    active_decoys_data.to_csv("../outputfile/double_dock_model_3_active_decoys.csv", index=False)

    end = time.time()
    cost = end - start
    print("Time cost for get label:", "%s seconds"%cost)
    logging.basicConfig(filename='../outputfile/time-cost-rdock-process.log', level=logging.INFO)
    logging.info("Time cost for get label: %s seconds"%cost)
