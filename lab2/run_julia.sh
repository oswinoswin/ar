#!/bin/bash
##przykladowe opcje dla polecenia sbatch
#SBATCH -p plgrid
#SBATCH -N 1
#SBATCH --ntasks-per-node=12
#SBATCH -J juliaRun
module add plgrid/tools/julia/1.0.0
cd $SLURM_SUBMIT_DIR
repeats = 10
for P in {1..12}
do
    for rep in {1..repeats}
    do
        time_distributed=$(julia -p $P  distributed.jl)
        time_pmap=$(julia -p $P  pmap.jl)
        echo "$P $time_distributed" >> distributed_results.txt
        echo "$P $time_pmap" >> pmap_results.txt
    done

done
