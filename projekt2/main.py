#!/usr/bin/env python
import numpy as np
from mpi4py import MPI
import argparse
import pandas as pd


def get_stars_number_per_rank(rank, N, world_size):
    to_calc = N // world_size
    max_buff_size = to_calc + 1
    if rank < N % world_size:
        return max_buff_size, max_buff_size
    return to_calc, max_buff_size


def squared_distance(x1, x2, y1, y2, z1, z2):
    return (x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2


def calculate_acceleration_to_star(this_x, this_y, this_z, M, x, y, z):
    ax = 0
    ay = 0
    az = 0
    for j, m in enumerate(M):
        squared_dist = squared_distance(this_x, x[j], this_y, y[j], this_z, z[j])
        if squared_dist == 0:
            continue
        ax = ax + (M[j]/squared_dist)*(x[j] - this_x)
        ay = ay + (M[j]/squared_dist)*(y[j] - this_y)
        az = az + (M[j]/squared_dist)*(z[j] - this_z)
    return ax, ay, az


def read_stars(start_index, stop_index):
    stars = pd.read_csv("stars")[start_index:stop_index]
    masses = np.array(stars["mass"])
    x_cords = np.array(stars["x_cords"])
    y_cords = np.array(stars["y_cords"])
    z_cords = np.array(stars["z_cords"])
    return masses, x_cords, y_cords, z_cords

comm = MPI.COMM_WORLD
world_size = comm.Get_size()
rank = comm.Get_rank()
N = 10

if rank == 0:
    parser = argparse.ArgumentParser()
    parser.add_argument("N", type=int)
    args = parser.parse_args()
    N = args.N  # number of stars

N = comm.bcast(N, root=0)
comm.Barrier()

to_calc, max_buf_size = get_stars_number_per_rank(rank, N, world_size)

# wszystkie procesy:
# losowanie gwiazd
# x_cords = np.random.rand(to_calc)
# masses = np.repeat(rank, to_calc)
# x_cords = np.repeat(rank, to_calc)
# y_cords = np.repeat(rank, to_calc)
# z_cords = np.repeat(rank, to_calc)
start_index = to_calc*rank if to_calc == max_buf_size else N - (world_size - rank)*to_calc
stop_index = start_index + to_calc
masses, x_cords, y_cords, z_cords = read_stars(start_index, stop_index)

# prepare buffer
x_buff = np.concatenate([x_cords, np.zeros(max_buf_size - to_calc)])
y_buff = np.concatenate([y_cords, np.zeros(max_buf_size - to_calc)])
z_buff = np.concatenate([z_cords, np.zeros(max_buf_size - to_calc)])
masses_buff = np.concatenate([masses, np.zeros(max_buf_size - to_calc)])

# accumulator
ax = np.zeros(to_calc)
ay = np.zeros(to_calc)
az = np.zeros(to_calc)

right_neighbour = (rank + 1) % world_size
left_neighbour = (world_size + rank - 1) % world_size


for it in range(world_size):
    comm.Send(masses_buff, dest=left_neighbour, tag=13)
    comm.Send(x_buff, dest=left_neighbour, tag=13)
    comm.Send(y_buff, dest=left_neighbour, tag=13)
    comm.Send(z_buff, dest=left_neighbour, tag=13)


    # calculate accelerations to every star owned by process
    for i, _ in enumerate(x_cords):
        tmp_ax, tmp_ay, tmp_az = calculate_acceleration_to_star(x_cords[i], y_cords[i], z_cords[i], masses_buff, x_buff, y_buff, z_buff)
        ax[i] = ax[i] + tmp_ax
        ay[i] = ay[i] + tmp_ay
        az[i] = az[i] + tmp_az

    masses_buff = np.zeros(max_buf_size)
    x_buff = np.zeros(max_buf_size)
    y_buff = np.zeros(max_buf_size)
    z_buff = np.zeros(max_buf_size)

    comm.Recv(masses_buff, source=right_neighbour, tag=13)
    comm.Recv(x_buff, source=right_neighbour, tag=13)
    comm.Recv(y_buff, source=right_neighbour, tag=13)
    comm.Recv(z_buff, source=right_neighbour, tag=13)

comm.Barrier()

print(f"Process {rank} results: {ax} {ay} {az}")

