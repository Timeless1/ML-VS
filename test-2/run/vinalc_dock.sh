#!/bin/bash
if [ ! -f  "recList.txt_ligList.txt.pdbqt.gz" ]
then
	mkdir ../outputfile
	id0=$(sbatch ../script/sub-vinalc-cnlong-openmpi.sbatch)
	for i in {1}
	do
		id0=${id0##* }
		id0=$(sbatch --dependency=afterany:$id0 vinalc_process.sbatch)
	done
else
	sbatch vinalc_process.sbatch
fi
