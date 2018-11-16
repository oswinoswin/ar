Pkg.add("Plots")
Pkg.add("Distributed")
Pkg.add("SharedArrays")
using Plots
using Distributed
using SharedArrays
Pkg.instantiate()
# punkt o współrzędnych (x,y) należy do zbioru Julii o parametrze  c 
# jeśli dla liczby zespolonej z=x+i*y
# ciąg zₙ₊₁=zₙ²+c , nie dąży do nieskończoności

# dążenie do nieskończoności sprawdzamy ustawiająć maksymalną liczbę iteracji i sprawdzając
# czy kolejne wyrazy ciągu nie przekroczą zadanego progu (tutaj 2) w tej (bądź mniejszej)
# liczbie iteracji

# funkcja sprawdzająca, czy punkt z należy do zbioru Julii o parametrze c
@everywhere function generate_julia(z; c=2, maxiter=200)
    for i=1:maxiter
        if abs(z) > 2
            return i-1
        end
        z = z^2 + c
    end
    maxiter
end

# obliczamy zbiór Julii na płaszczyźnie punktów od-do.

 function calc_julia!(julia_set, xrange, yrange; maxiter=2000, height=400, width_start=1, width_end=400)
  @distributed
  for x=width_start:width_end
        for y=1:height
            z = xrange[x] + 1im*yrange[y]
            julia_set[x, y] = generate_julia(z, c=-0.70176-0.3842im, maxiter=maxiter)
        end
  end

 end

@everywhere calc_julia_point(julia_set, xrange, yrange; x, y, maxiter)
    z = xrange[x] + 1im*yrange[y]
    julia_set[x, y] = generate_julia(z, c=-0.70176-0.3842im, maxiter=maxiter)
end

# główna funkcja 

 function calc_julia_main(h,w)
  # ustawiamy płaszczyznę
   xmin, xmax = -0.5,0.5
   ymin, ymax = -0.5,0.5
   xrange = xmin:(xmax-xmin)/(w-1):xmax  
   yrange = ymin:(ymax-ymin)/(h-1):ymax
    
   julia_set = SharedArray{Int64,2}(w, h)
   # wywołujemy w celu kompilacji na jednym wierszu:
    calc_julia!(julia_set, xrange, yrange, height=h,width_start=1, width_end=1)
  
   # obliczamy
   @time calc_julia!(julia_set, xrange, yrange, height=h,width_start=1, width_end=w)
    
    # rysujemy
   pl=Plots.heatmap(xrange, yrange, julia_set)
   
   return pl
endf_plot.set_ylabel('serial fraction')

