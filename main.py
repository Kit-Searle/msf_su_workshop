# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 19:41:51 2024

@author: ksearle
"""
#%% Import necessary modules and initialize environment
from class_dwellings import Dwellings # Classes for dwellings
from class_candidates import Candidates
from obj_func_code import process_raster
from plots import plot_result_with_map, plot_dwellings, plot_candidates, plot_candidate_raster  # Custom plotting function
from pathlib import Path
from zipfile import ZipFile

#%% Set working directory and define data paths
cwd = Path.cwd()  # or your specific project path
data_folder = cwd / "data" 

temp_data_folder = cwd / "data" / "temp_data"
plots_folder = cwd / "plots" 

folder_names = ["v_b", "v_i", "v_t"]

for name in folder_names:
    folder = data_folder / name
    zip_file = data_folder / f"{name}.zip"

    if folder.exists():
        print(f"✅ Folder exists: {folder}")
        continue

    if zip_file.exists():
        print(f"📦 Unzipping: {zip_file.name} …")
        with ZipFile(zip_file, "r") as z:
            z.extractall(data_folder)
        print(f"✅ Unzipped → {folder}")
    else:
        print(f"❌ Neither folder nor zip found for: {name}")

# Check if it exists, create if not
temp_data_folder.mkdir(parents=True, exist_ok=True)
plots_folder.mkdir(parents=True, exist_ok=True)

#%%
dwellings = Dwellings(data_folder)
dwellings.load_data()
plot_dwellings(dwellings)

candidates = Candidates(data_folder)
plot_candidates(candidates)

# This may take a few mins
candidates.load_data()

#%%

plot_candidate_raster(candidates,3998,'time')

#%%
candidates.get_voronoi()
candidates.plot_graph()

candidates.get_nearest_neighbours(3998, 2)

#%%

build = [3998, 28167]
process_raster(candidates, dwellings, build)
plot_result_with_map(build, candidates, dwellings, 'test')