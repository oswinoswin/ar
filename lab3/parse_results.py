filename = "channels_results.txt"
outfilename = "channels.csv"

with open(filename,"r") as results, open(outfilename, "w") as outfile:
    outfile.write(f"procs,time,allocations\n")
    for line in results:
        line = line.split()
        print(line)
        procs = int(line[0])
        time = float(line[1])
        allocations = float(line[3][1:])
        print(f"{procs}, {time}, {allocations}")
        outfile.write(f"{procs},{time},{allocations}\n")