#!/bin/bash
if [ ! -f "../outputfile/result_1.sd" ]
then	
	line=$(awk '{print NR}' ../outputfile/vinalc_top20.txt|tail -n1)
	result=$[line/30]
	#result=$[result+1]
	source /lustre1/iip_pkuhpc/iip_test/apps/source/docking.sh
	sdsplit ../outputfile/compounds_rdock.sd -o../outputfile/ -$result
	obabel -imol2 ../inputfile/ligand.mol2 -osd -O ../outputfile/ligand.sd
	cp -r ../confile/protein.prm ./
	rbcavity -was -d -r protein.prm
	id0=$(sbatch ../script/sub-cnnl.sbatch)
	for i in {1}
	do
		id0=${id0##* }
		id0=$(sbatch --dependency=afterany:$id0 rdock_process.sbatch)
	done
else
	sbatch rdock_process.sbatch
fi
