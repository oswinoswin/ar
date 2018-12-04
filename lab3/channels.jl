using Distributed
using SharedArrays
# using Plots
# Pkg.instantiate()

function generate_julia(z; c=2, maxiter=200)
    for i=1:maxiter
        if abs(z) > 2
            return i-1
        end
        z = z^2 + c
    end
    maxiter
end

 function calc_julia!(julia_set, xrange, yrange; maxiter=2000, height=400, width_start=1, width_end=400)

  for x=width_start:width_end
        for y=1:height
            z = xrange[x] + 1im*yrange[y]
            julia_set[x, y] = generate_julia(z, c=-0.70176-0.3842im, maxiter=maxiter)
        end
  end

 end


# zdalny kanał przekazujący numery zadańM
const jobs = RemoteChannel(()->Channel{Int}(32));

# zdalny kanał przekazujący wyniki
const results = RemoteChannel(()->Channel{Tuple}(32));

# funkcja wykonująca pewną (symulowaną sleepem) "pracę"
 @everywhere function do_work(jobs, results) # define work function everywhere
           while true
               job_id, task_width = take!(jobs)
               exec_time = rand()
               sleep(exec_time) # tu powinno być liczenie julii
               #calc_julia!(julia_set, xrange, yrange, height=h,width_start=1, width_end=w)
               put!(results, (1:job_id, exec_time, myid()))
           end
  end

# funkcja wkładająca  do kanału numery "prac"

function make_jobs(n, task_width)
           for i in 1:n-1
               put!(jobs, (i, task_width))
           end
           put!(jobs, (n, task_width))
end;


function calc_julia_main(h,w)
  # ustawiamy płaszczyznę
   xmin, xmax = -0.5,0.5
   ymin, ymax = -0.5,0.5
   xrange = xmin:(xmax-xmin)/(w-1):xmax
   yrange = ymin:(ymax-ymin)/(h-1):ymax

   julia_set = SharedArray{Int64,2}(w, h)
   # wywołujemy w celu kompilacji na jednym wierszu:
    calc_julia!(julia_set, xrange, yrange, height=h,width_start=1, width_end=1)

#    # obliczamy
#    @time calc_julia!(julia_set, xrange, yrange, height=h,width_start=1, width_end=w)
    nworkers() |> println
    n_tasks = 10*nworkers()
    n_tasks |> println
    task_width = w/n_tasks
    task_width |> println
    n_tasks = 10
    @async make_jobs(n_tasks, task_width);

    # starujemy zdalne zadania

    for p in workers() # start tasks on the workers to process requests in parallel
               remote_do(do_work, p, jobs, results)
    end

    # wypisujemy wyniki
    n = n_tasks
    while n > 0 # print out results
               job_id, exec_time, where = take!(results)
               println("$job_id finished in $(round(exec_time; digits=2)) seconds on worker $where")
               n = n - 1
    end

    # przesyłamy wiadomośc o zamknięciu do zdalnych procesów
    finalize(jobs)
    finalize(results)



#     # rysujemy
#    pl=Plots.heatmap(xrange, yrange, julia_set)

#    return pl
end

calc_julia_main(10, 10)