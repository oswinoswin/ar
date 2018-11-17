#!/bin/bash
##przykladowe opcje dla polecenia sbatch
#SBATCH -p plgrid
#SBATCH -N 1
#SBATCH --ntasks-per-node=12
#SBATCH -J juliaRun
module add plgrid/tools/julia/1.0.0
cd $SLURM_SUBMIT_DIR
for P in {1..12}
do
    julia -p $P  distributed.jl >> distributed_time.txt
    julia -p $P  pmap.jl >> pmap_time.txt
done
