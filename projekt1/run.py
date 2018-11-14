#!/usr/bin/env python
import os
import commands


N = [100, 200, 300]
procs = list(range(1, 9))

filename='temperature_out.csv'
with open(filename, 'wb') as f_out:
    f_out.write("points,procesors,time\n")
    for n in N:
        for proc in procs:

            run_cmd = ''' mpiexec -machinefile a8 -np {} ./temperature.py {}'''.format(proc, n).strip()
            print(run_cmd)
            time = commands.getoutput(run_cmd).split(' ')[0]
            print(time)
            f_out.write("{},{},{}\n".format(str(n), str(proc), str(time)))
print("done")