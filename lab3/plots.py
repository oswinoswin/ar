import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("channels.csv")

## plot mean time for pmap
mean_time = df.groupby(["procs"]).describe()["time"][["mean"]]
y = mean_time["mean"].values
x = np.arange(1,13)
plt.bar(x, y)
plt.title("Mean time")
plt.xlabel("Number of processors")
plt.ylabel("Time [s]")
plt.savefig("plots/channels_time.png")
plt.clf()

## plot speedup
time = np.array(y)
time_0 = time[0]
speedup = time_0/time
y = speedup
plt.bar(x, y)
plt.title("Speedup")
plt.xlabel("Number of processors")
plt.ylabel("Speedup")
plt.savefig("plots/channels_speedup.png")
plt.clf()

## plot efficiency
time = np.array(y)
time_0 = time[0]
efficiency = speedup/x
y = efficiency
plt.bar(x, y)
plt.title("Efficiency")
plt.xlabel("Number of processors")
plt.ylabel("Efficiency")
plt.savefig("plots/channels_efficiency.png")
plt.clf()

# print allocations
allocations = df.groupby(["procs"]).describe()["allocations"][["mean"]]
allocations = allocations["mean"].values
y = allocations
plt.bar(x, y)
plt.title("Allocations")
plt.xlabel("Number of processors")
plt.ylabel("Allocations")
plt.savefig("plots/channels_allocations.png")
plt.clf()


