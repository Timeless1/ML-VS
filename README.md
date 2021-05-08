## Double Dock For Chemprop Model-Training

 **简述：**

* 接口调用vinalc和rdock程序，分别对给定化合物库进行双对接筛选。
* DOCK_1结束后，按照对接得分排序取top_20%进行DOCK_2对接；

* DOCK_2结束后，回收数据用于模型的训练及预测；



## Requirements

vinalc;

rdock2013.1;

chemprop;

Open Babel 3.0.0;

cuda >= 8.0;

cuDNN;



### Installation

---

### Option 1: Conda

The easiest way to install the `chemprop` dependencies is via conda. Here are the steps:

1. `cd /path/to/chemprop`
2. `conda env create -f environment.yml`
3. `conda activate chemprop` (or `source activate chemprop` for older versions of conda)

Note that on machines with GPUs, you may need to manually install a GPU-enabled version of PyTorch by following the instructions [here](https://pytorch.org/get-started/locally/).

### Option 2: Docker

Docker provides a nice way to isolate the `chemprop` code and environment. To install and run our code in a Docker container, follow these steps:

1. `cd /path/to/chemprop`
2. `docker build -t chemprop .`
3. `docker run -it chemprop:latest /bin/bash`

Note that you will need to run the latter command with nvidia-docker if you are on a GPU machine in order to be able to access the GPUs.





## 文件命名方式

* **ReIndex中的命名**

|    对象    |             命名方式             |
| :--------: | :------------------------------: |
|   active   |    active0001(英文+四位数字)     |
|   decoys   |   decoys0000001(英文+七位数字)   |
|  chemDiv   | ligand_0000001(ligand_+七位数字) |
| smiles.csv |      [ UniqueID , smiles ]       |



* **对接前文件准备及命名方式**

  |           文件            |                             路径                             |                     描述                      |              命名               |
  | :-----------------------: | :----------------------------------------------------------: | :-------------------------------------------: | :-----------------------------: |
  |       protein.pdbqt       |                           ../temp/                           |         用于vinalc对接的蛋白形式文件          |          protein.pdbqt          |
  |       protein.mol2        |                           ../temp/                           |          用于rdock对接的蛋白形式文件          |          protein.mol2           |
  |        ligand.mol2        |                           ../temp/                           |    原配体分子，用于确定rdock对接的口袋中心    |           ligand.mol2           |
  |        对接分子库         |                 ../temp/compounds_all.pdbqt                  |   用于筛选的库pdbqt格式(包含active/decoys)    |       compounds_all.pdbqt       |
  |    对接分子库单个文件     | /home/iip_pkuhpc/iip_test/lustre3/mawei/AI/score-consensus/data/single_mol2_chemDiv/ |      用于筛选的库mol2格式的分子单个文件       |       single_mol2_chemDiv       |
  | active_decoys_single_file |                ../active_decoys_single_mol2/                 |          active/decoys分子的单个文件          |    active_decoys_single_file    |
  |        smiles_all         |                           ../temp/                           | 所有对接化合物的smiles信息(包括active/decoys) |         smiles_all.csv          |
  |        geoList.txt        |                           ../temp/                           |          指定蛋白口袋中心及Grid尺度           |           geoList.txt           |
  |        recList.txt        |                           ../temp/                           |                 指定蛋白路径                  | recList.txt（./protein.pdbqt)） |
  |        ligList.txt        |                           ../temp/                           |              指定对接分子库路径               | ligList(./compounds_all.pdbqt)  |
  |        protein.prm        |                           ../temp/                           |              rdock对接的参数文件              |          protein.prm()          |



* **中间文件的命名**

|        文件        |                       描述                       |            命名            |
| :----------------: | :----------------------------------------------: | :------------------------: |
|     key_value      | 记录排序好的每个分子的第一个得分信息(vinalc结果) |       key_value.txt        |
|    vinalc_top20    |   记录vinalc的top_20%的UniqueID信息的UniqueID    |      vinalc_top20.txt      |
| vinalc_top_20.mol2 |          vinalc的top_20%分子的mol2格式           |     vinalc_top_20.mol2     |
| compounds_rdock.sd |      用于rdock对接的vinalc的top_20%的sd格式      |     compounds_rdock.sd     |
|       model/       |          vinalc的结果的单个分子切分文件          | model/ligand_0000001.pdbqt |



* 运行方式（/home/iip_pkuhpc/iip_test/lustre3/mawei/AI/score-consensus/test/consensus-score/test_file/code-1/test-7)

1. 整体运行：

```
[ shell temp]$    ./vinalc_dock.sh
```

2. 单个脚本运行：

```
step1:vinalc对接
[shell temp]$	 sbatch sub-vinalc-cnlong-openmpi.sbatch    (提交后等待结束，sq命令查看运行状态)

step2:vinalc对接后处理
[shell temp]$	 python sort_for_vinalc_pdbqt.py

step3:rdock对接
[shell temp]$	 sbatch sub-cnnl.sbatch				(提交后等待结束，sq命令查看运行状态)

step4:rdock对接后处理
[shell temp]$	 python get_label.py
```

3. 结果回传需求（12个文件，每个100k—5MB左右，总共<= 30MB）

```
double_dock_model_1_train.csv				double_dock_model_1_active_decoys.csv
double_dock_model_2_train.csv				double_dock_model_3_active_decoys.csv
double_dock_model_2_train.csv				double_dock_model_3_active_decoys.csv

vinalc_model_1_train.csv					vinalc_model_1_active_decoys.csv
vinalc_model_2_train.csv					vinalc_model_2_active_decoys.csv
vinalc_model_3_train.csv					vinalc_model_3_active_decoys.csv
```

4. 清理文件

```
全部文件(包括对接产生的文件)
[shell temp]$	 ./clean_all.sh

部分中间文件（对接后处理过程中产生的文件）
[shell temp]$	 ./clean_partial.sh


```



## 文件结构调整（2020_07_22）

---

|   confile   |      inputfile      |              script              |         work          | outputfile |
| :---------: | :-----------------: | :------------------------------: | :-------------------: | ---------- |
| ligList.txt | compounds_all.pdbqt | sub-vinalc-cnlong-openmpi.sbatch |       rdock.sh        | ——         |
| protein.prm |     geoList.txt     |         sub-cnnl.sbatch          | rdock_process.sbatch  | ——         |
| recList.txt |     ligand.mol2     |     sort_for_vinalc_pdbqt.py     |    vinalc_dock.sh     | ——         |
|             |    protein.mol2     |         rdock_future.py          | vinalc_process.sbatch | ——         |
|             |    protein.pdbqt    |           get_label.py           |     clean_all.sh      | ——         |
|             |   smiles_all.csv    |                                  |                       | ——         |



## Run

---

```
[ shell ../work ]$    ./vinalc_dock.sh
```

