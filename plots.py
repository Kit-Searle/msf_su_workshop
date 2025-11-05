# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 13:18:59 2024

@author: ksearle
"""
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap, LinearSegmentedColormap
import contextily as ctx  # For adding basemaps to geographic data plots
from obj_func_code import process_raster_for_visulisation  # Custom function for raster processing
import rasterio  # For working with raster data
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import numpy as np
import os

def plot_dwellings(dwellings):
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    
    
    with rasterio.open(dwellings.main_raster_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': 'EPSG:4326',
            'transform': transform,
            'width': width,
            'height': height
        })
        
        # Initialize reprojected raster array
        reprojected_result_raster = np.empty((height, width), dtype=np.float32)
        
        # Perform reprojection
        reproject(
            source=dwellings.main_data,
            destination=reprojected_result_raster,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs='EPSG:4326',
            resampling=Resampling.nearest
        )

    

    # Define extent for plotting reprojected rasters
    raster_extent = [
        transform[2], 
        transform[2] + transform[0] * reprojected_result_raster.shape[1],
        transform[5] + transform[4] * reprojected_result_raster.shape[0],
        transform[5]
    ]
    
    # Create color map for result raster
    base_cmap1 = LinearSegmentedColormap.from_list('black_to_red', ['red', 'black'])
    base_colors1 = base_cmap1(np.arange(base_cmap1.N))
    alpha_channel1 = np.ones(base_colors1.shape[0])
    alpha_channel1[0] = 0  # Set lowest value to transparent
    base_colors1[:, -1] = alpha_channel1
    cmap1 = ListedColormap(base_colors1)
    
    # Plot reprojected result raster as a heatmap
    ax.imshow(
        reprojected_result_raster, cmap=cmap1,
        norm=BoundaryNorm(boundaries=np.linspace(np.min(reprojected_result_raster), np.max(reprojected_result_raster), 256), ncolors=256),
        extent=raster_extent, alpha=1,zorder=10 )
    
    ctx.add_basemap(ax, crs= 'EPSG:4326', zorder=0)
    
    ax.set_title(f'dwellings')
    
def plot_candidates(candidates):
 
    candidate_points = [Point(xy) for xy in candidates.all_candidates.values()]
    candidate_indices = list(candidates.all_candidates.keys())
    
    candidate_gdf = gpd.GeoDataFrame(
        geometry=candidate_points,
        index=candidate_indices,
        crs='EPSG:32738'
    ).to_crs(epsg=4326)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    

    
    # Plot candidate points in gray
    candidate_gdf.plot(ax=ax, marker='o', color='grey', markersize=1, alpha=0.5)
    
    # Add background basemap
    ctx.add_basemap(ax, crs=candidate_gdf.crs.to_string())
    ax.set_title('candidates')
    
def plot_candidate_raster(candidates,candidate,raster):
    
    map_to_file = {'reduction': 'v_i', 'coverage' : 'v_b', 'time': 'v_t'}
 
    candidate_points = [Point(xy) for xy in candidates.all_candidates.values()]
    candidate_indices = list(candidates.all_candidates.keys())
    
    candidate_gdf = gpd.GeoDataFrame(
        geometry=candidate_points,
        index=candidate_indices,
        crs='EPSG:32738'
    ).to_crs(epsg=4326)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    

    
    # Plot candidate points in gray
    candidate_gdf.plot(ax=ax, marker='o', color='grey', markersize=1, alpha=0.5)
    
    # Add background basemap
    ctx.add_basemap(ax, crs=candidate_gdf.crs.to_string())
    
    location_tif = candidates.data_file / map_to_file[raster] / f'dry_walk_site_{candidate}.tif'
    reprojected_tif_path = candidates.data_file / 'temp_data' / f'reprojected_{candidate}.tif'

    hold_gdf= gpd.GeoDataFrame(geometry=candidate_gdf.loc[candidate], crs='EPSG:4326')
    hold_gdf.plot(ax=ax, marker='x', color='black', markersize=20, alpha=0.5)
    with rasterio.open(location_tif) as src:
        transform, width, height = calculate_default_transform(
            src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': 'EPSG:4326',
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(reprojected_tif_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs='EPSG:4326',
                    resampling=Resampling.nearest)

    # Display the reprojected TIF data on the map
    with rasterio.open(reprojected_tif_path) as src:
        show(src, ax=ax, alpha=0.4)
    
    ax.set_title(f'candidate {candidate} with raster {raster}')
    
    
    

def plot_result_with_map(individual,candidates, dwellings, name):
    """
    Plots geographic information and analysis results over a basemap.

    This function generates a map overlay of candidate locations and raster-based analysis results.
    Each individual's data is processed and plotted with relevant transformations to visualize its 
    geographic impact. 

    Parameters:
        individual (list): List of individual locations (typically represented by TIF files) to visualize.
        candidate_manager (CandidateManager): Manager object containing candidate locations and geometry.
    """
    
    # Retrieve and set up candidate GeoDataFrame with required CRS transformations
    candidate_points = [Point(xy) for xy in candidates.all_candidates.values()]
    candidate_indices = list(candidates.all_candidates.keys())
    
    candidate_gdf = gpd.GeoDataFrame(
        geometry=candidate_points,
        index=candidate_indices,
        crs='EPSG:32738'
    ).to_crs(epsg=4326)
    
    cwd = os.getcwd()
    # Set up the plotting figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot candidate points in gray
    candidate_gdf.plot(ax=ax, marker='o', color='grey', markersize=1, alpha=0.5)
    
    # Add background basemap
    ctx.add_basemap(ax, crs=candidate_gdf.crs.to_string())
    
    # Process raster data for analysis result
    results, rasters = process_raster_for_visulisation(candidates, dwellings, individual)
    
    # Open and reproject primary result raster to EPSG:4326
    with rasterio.open(dwellings.main_raster_path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': 'EPSG:4326',
            'transform': transform,
            'width': width,
            'height': height
        })
        
        # Initialize reprojected raster array
        reprojected_result_raster = np.empty((height, width), dtype=np.float32)
        
        # Perform reprojection
        reproject(
            source=rasters[0],
            destination=reprojected_result_raster,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs='EPSG:4326',
            resampling=Resampling.nearest
        )

    

    # Define extent for plotting reprojected rasters
    raster_extent = [
        transform[2], 
        transform[2] + transform[0] * reprojected_result_raster.shape[1],
        transform[5] + transform[4] * reprojected_result_raster.shape[0],
        transform[5]
    ]
    
    # Create color map for result raster
    base_cmap1 = LinearSegmentedColormap.from_list('black_to_red', ['red', 'black'])
    base_colors1 = base_cmap1(np.arange(base_cmap1.N))
    alpha_channel1 = np.ones(base_colors1.shape[0])
    alpha_channel1[0] = 0  # Set lowest value to transparent
    base_colors1[:, -1] = alpha_channel1
    cmap1 = ListedColormap(base_colors1)
    
    # Plot reprojected result raster as a heatmap
    heatmap1 = ax.imshow(
        reprojected_result_raster, cmap=cmap1,
        norm=BoundaryNorm(boundaries=np.linspace(np.min(reprojected_result_raster), np.max(reprojected_result_raster), 256), ncolors=256),
        extent=raster_extent, alpha=1)
    
    # Overlay TIF files for each location in the individual
    for location in individual:
        location_tif = candidates.data_file / 'v_i'/ f'dry_walk_site_{location}.tif'
        reprojected_tif_path = candidates.data_file / 'temp_data' / f'reprojected_{location}.tif'

        hold_gdf= gpd.GeoDataFrame(geometry=candidate_gdf.loc[location], crs='EPSG:4326')
        hold_gdf.plot(ax=ax, marker='x', color='black', markersize=20, alpha=0.5)
        with rasterio.open(location_tif) as src:
            transform, width, height = calculate_default_transform(
                src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': 'EPSG:4326',
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(reprojected_tif_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs='EPSG:4326',
                        resampling=Resampling.nearest)

        # Display the reprojected TIF data on the map
        with rasterio.open(reprojected_tif_path) as src:
            show(src, ax=ax, alpha=0.4)

    # Save the final map plot to PDF
    output_path =  cwd+rf'\plots\{name}.pdf'
    plt.savefig(output_path, transparent=True, pad_inches=0.1, bbox_inches='tight')
