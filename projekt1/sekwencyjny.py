import numpy as np

# constants
g = 1
l = 15
h = 1


N = 5
max_iter = 100
T = np.random.rand(N,N)

T[0,:] = 0
T[:,0] = 0
T[-1,:] = 0
T[:, -1] = 0

def calculate_temperature(y, x):
    t_g = T[y - 1, x]
    t_d = T[y + 1, x]
    t_l = T[y, x - 1]
    t_r = T[y, x + 1]
    T[y, x] = (t_g + t_d + t_l + t_r + (g*h)/l)/4

print(T)

for it in range(max_iter):
    for row in range(1,N-1):
        for col in range(1, N-1):
            calculate_temperature(row, col)
print(T)
