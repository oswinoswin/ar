#!/home/oswin/anaconda3/bin/python
import numpy as np
from mpi4py import MPI
import argparse
import matplotlib.pyplot as plt

def get_num_rows_to_calc(N, size, rank):
    if rank < N % size:
        return N // size + 1
    else:
        return  N//size

def get_start_row(N, size, rank):
    if rank < N % size:
        return rank*get_num_rows_to_calc(N, size, rank)
    else:
        return  N - (size - rank)*get_num_rows_to_calc(N, size, rank)

# constants
g = 1
l = 15
h = 1

N = 1000000
max_iter = 3

def calculate_temperature(tab, y, x, N):
    if x == 0 or y == 0 or x == N-1 or y == N-1:
        return 0.
    t_g = tab[y - 1, x]
    t_d = tab[y + 1, x]
    t_l = tab[y, x - 1]
    t_r = tab[y, x + 1]
    return (t_g + t_d + t_l + t_r + (g*h)/l)/4

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


if rank == 0:
    parser = argparse.ArgumentParser()
    parser.add_argument("N")
    parser.add_argument("max_iter")
    args = parser.parse_args()
    N = int(args.N)
    max_iter = int(args.max_iter)


    T = np.random.rand(N, N)
    T[0, :] = 0
    T[:, 0] = 0
    T[-1, :] = 0
    T[:, -1] = 0
    plt.imshow(T)
    plt.title("before")
    plt.colorbar()
    plt.show()


N = comm.bcast(N, root=0)
max_iter = comm.bcast(max_iter, root=0)
comm.Barrier()

if rank < N%size:
    rows_to_calculate = N//size + 1
    start_row = rank*rows_to_calculate
else:
    rows_to_calculate = N//size
    start_row = N - (size - rank)*rows_to_calculate

if rank != 0:
    T = np.empty(N * N, dtype='d')
    T = np.reshape(T, (N, N))

split_sizes = [ get_num_rows_to_calc(N, size, x)*N for x in range(size)]
displacements = [ get_start_row(N, size, x)*N for x in range(size)]

for i in range(max_iter):
    comm.Bcast(T, root=0) # broadcast the array from rank 0 to all others
    #T[start_row:start_row + rows_to_calculate,:] = rank
    for y in range(start_row, start_row + rows_to_calculate):
        for x in range(N):
            T[y, x] = calculate_temperature(T, y, x, N)

    output_table = T[start_row:start_row + rows_to_calculate,:]


    recvbuf = None
    if rank == 0:
        recvbuf = np.zeros([N,N], dtype='d')

    comm.Barrier()
    comm.Gatherv(output_table, [recvbuf, split_sizes, displacements, MPI.DOUBLE], root=0)

    if rank == 0:
        T = recvbuf

if rank == 0:
    print(T)
    plt.imshow(T)
    plt.title("after")
    plt.colorbar()
    plt.show()
