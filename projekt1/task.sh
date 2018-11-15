#!/bin/bash -l
## Nazwa zlecenia
#SBATCH -J MPITest
## Liczba alokowanych węzłów
#SBATCH -N 1
## Liczba zadań per węzeł (domyślnie jest to liczba alokowanych rdzeni na węźle)
#SBATCH --ntasks-per-node=12
## Ilość pamięci przypadającej na jeden rdzeń obliczeniowy (domyślnie 4GB na rdzeń)
#SBATCH --mem-per-cpu=4GB
## Maksymalny czas trwania zlecenia (format HH:MM:SS)
#SBATCH --time=01:00:00
## Nazwa grantu do rozliczenia zużycia zasobów
#SBATCH -A <grant_id>
## Specyfikacja partycji
#SBATCH -p plgrid-testing
## Plik ze standardowym wyjściem
#SBATCH --output="task_output.out"
## Plik ze standardowym wyjściem błędów
#SBATCH --error="task_error.err"

srun /bin/hostname

## Zaladowanie modulu IntelMPI w wersji domyslnej
module add plgrid/tools/impi

## przejscie do katalogu z ktorego wywolany zostal sbatch
cd $SLURM_SUBMIT_DIR

repeats=10
max_process=12

echo "proc,N,time" > run_output.csv

for N in 50 100 200 300 400 500 1000
do
    for proc in {1..12}
    do
        total_time=0
        for rep in {1..repeats}
        do
            res=$(mpiexec -np 2 ./temperature.py $N)
            echo $res
            total_time=$(bc <<< "scale=5;$total_time+$res")
        done
        total_time=$(bc <<< "scale=5;$total_time/10")
        echo "$proc, $N, $total_time" >> run_output.csv

    done
done

