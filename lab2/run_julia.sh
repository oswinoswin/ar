#!/bin/bash
##przykladowe opcje dla polecenia sbatch
#SBATCH -p plgrid
#SBATCH -N 1
#SBATCH --ntasks-per-node=12
module add plgrid/tools/julia/1.0.0

for P in {1..12}
do
    julia -p 12  distributed.jl >> distributed_time.txt
    julia -p 12  pmap.jl >> pmap_time.txt
done