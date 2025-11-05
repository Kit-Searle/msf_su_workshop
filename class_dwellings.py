# -*- coding: utf-8 -*-
"""
Created on Wed May 14 14:26:14 2025

@author: ksearle
"""

import rasterio
import numpy as np


class Dwellings:
    def __init__(self,data):
        self.main_raster_path = data / "dwellings_count_utm_clipped.tif"
        self.isolation_path = data / "dwellings_isolation_norm_utm.tif"
        
    def load_data(self):   
        with rasterio.open(self.main_raster_path) as main_src:
            self.main_extent,  self.main_transform,  self.main_width,  self.main_height = main_src.bounds, main_src.transform, main_src.width, main_src.height

            
            self.main_data = main_src.read(1)
            self.main_data[self.main_data < 0] = 0
            
        with rasterio.open(self.isolation_path) as src:
            self.isolation_data = src.read(1)   # read raw raster values
            self.isolation_data = np.nan_to_num(self.isolation_data, nan=0)   # replace NaN with 0
            
    def get_coordinates(self, r, c):
        x, y = rasterio.transform.xy(self.main_transform, r, c, offset='center')
        return [x,y]
