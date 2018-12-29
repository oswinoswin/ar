import pandas as pd
import numpy as np


stars = pd.DataFrame(columns=["mass", "x_cord", "y_cord", "z_cord"])
stars_num = 1000
stars["mass"] = np.random.rand(stars_num)
stars["x_cord"] = np.random.rand(stars_num)
stars["y_cord"] = np.random.rand(stars_num)
stars["z_cord"] = np.random.rand(stars_num)

stars.to_csv("stars.csv")