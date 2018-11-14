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

def send_to_neighbors(rank, t, world_size):
    if rank != world_size - 1:
        send_to_next = t[-2, :]  # send last calculated by rank 0
        comm.Send(send_to_next, dest=rank + 1, tag=13)

    if rank != 0:
        send_to_prev = t[1, :]
        comm.Send(send_to_prev, dest=rank - 1, tag=13)

def recieve_from_neighbors(rank, t, world_size, N):
    if rank != world_size - 1:
        recv_from_next = np.empty(N, dtype=np.float64)
        comm.Recv(recv_from_next, source=rank + 1, tag=13)
        t[-1, :] = recv_from_next

    if rank != 0:
        recv_from_prev = np.empty(N, dtype=np.float64)
        comm.Recv(recv_from_prev, source=rank - 1, tag=13)
        t[0, :] = recv_from_prev

# constants
g = 1
l = 15
h = 1


N = 1000000
max_iter = 3

def calculate_temperature(tab, y, x):
    t_g = tab[y - 1, x]
    t_d = tab[y + 1, x]
    t_l = tab[y, x - 1]
    t_r = tab[y, x + 1]
    return (t_g + t_d + t_l + t_r + (g*h)/l)/4

def main():
    comm = MPI.COMM_WORLD
    world_size = comm.Get_size()
    rank = comm.Get_rank()

    if rank == 0:
        parser = argparse.ArgumentParser()
        parser.add_argument("N")
        parser.add_argument("max_iter")
        args = parser.parse_args()
        N = int(args.N)
        max_iter = int(args.max_iter)

        if world_size == 1:
            T = np.zeros([N, N], dtype='d')
            for it in range(max_iter):
                for row in range(1, N - 1):
                    for col in range(1, N - 1):
                        T[row,col] =  calculate_temperature(T, row, col)
            plt.imshow(T)
            plt.show()
            return


    N = comm.bcast(N, root=0)
    max_iter = comm.bcast(max_iter, root=0)
    comm.Barrier()

    if rank < N%world_size:
        rows_to_calculate = N // world_size + 1
        start_row = rank*rows_to_calculate
    else:
        rows_to_calculate = N // world_size
        start_row = N - (world_size - rank) * rows_to_calculate

    ## initialize table
    if rank == 0:
        t = np.random.rand(rows_to_calculate + 1, N)
        t[0,:] = 0

    elif rank == world_size - 1:
        t = np.random.rand(rows_to_calculate + 1, N)
        t[-1,:] = 0

    else:
        t = np.random.rand(rows_to_calculate + 2, N)

    t[:,0] = 0
    t[:,-1] = 0


    send_to_neighbors(rank, t, world_size)


    y_size, x_size = t.shape

    for i in range(max_iter):
        recieve_from_neighbors(rank, t, world_size, N)
        for y in range(1, y_size-1):
            for x in range(1, x_size-1):
                t[y, x] = calculate_temperature(t, y, x)

        send_to_neighbors(rank, t, world_size)

    recieve_from_neighbors(rank, t, world_size, N)
    comm.Barrier()

    ## gather results
    split_sizes = [ get_num_rows_to_calc(N, world_size, x)*N for x in range(world_size)]
    displacements = [ get_start_row(N, world_size, x)*N for x in range(world_size)]
    displacements[0] = N

    recvbuf = None
    if rank == 0:
        recvbuf = np.zeros([N, N], dtype='d')
        output_table = t
    if rank == world_size -1:
        output_table = t[1:,:]
    else:
        output_table = t[1:-1,:]

    comm.Gatherv(output_table, [recvbuf, split_sizes, displacements, MPI.DOUBLE], root=0)

    if rank == 0:
        plt.imshow(recvbuf)
        plt.show()
        print(recvbuf.shape)
        print(split_sizes)
        print(displacements)

main()


