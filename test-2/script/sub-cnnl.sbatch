#!/bin/bash
#SBATCH -J rdock
#SBATCH -p cn-long
#SBATCH -N 1 
#SBATCH -o ../outputfile/rdock_%j.out
#SBATCH -e ../outputfile/rdock_%j.err
#SBATCH --no-requeue
#SBATCH -A iip_g1
#SBATCH --qos=iipcnl
##SBATCH -c 20
#SBATCH --ntasks-per-node=20
#pkurun  ./run-mpi-openmpi.sh

source /lustre1/iip_pkuhpc/iip_test/apps/source/docking.sh

source /appsnew/source/openmpi-4.0.1-gcc8.3.0.sh
hosts=`scontrol show hostname $SLURM_JOB_NODELIST` ;echo $hosts

#. /appsnew/source/openmpi-4.0.1-gcc.sh
#mpirun  -n $SLURM_NTASKS -quiet --mca pml ob1 --mca btl_openib_allow_ib true ./beijixing
#$SLURM_NTASKS为使用的cpu数，可以自己定义

echo $SLURM_NTASKS

source /lustre1/iip_pkuhpc/iip_test/apps/source/docking.sh
/lustre3/iip_pkuhpc/iip_test/cyxu/anaconda3/bin/python ../script/rdock-future.py

