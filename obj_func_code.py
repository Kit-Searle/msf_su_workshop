# -*- coding: utf-8 -*-
"""
Created on Fri May 16 14:09:28 2025

@author: ksearle
"""

import numpy as np           
              

def create_blank_raster(main_extent, main_transform, main_width, main_height):
    dtype = np.float32  # Adjust dtype if needed
    blank_raster = np.zeros((main_height, main_width), dtype=dtype)
    return blank_raster
                   
def process_raster(candidates, dwellings, selected_raster_numbers):
    # Load main raster extent and create blank raster
    composite_raster_reduction = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
    composite_raster_coverage = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
    
    # Iterate through selected raster numbers
    for raster_number in selected_raster_numbers:
        window = candidates.candidate_data[raster_number]['window']
        candidate_raster_reduction = candidates.candidate_data[raster_number]['reduction']
        blank_raster_reduction = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
        blank_raster_reduction[window.row_off:window.row_off + window.height, window.col_off:window.col_off + window.width] = candidate_raster_reduction
        
        composite_raster_reduction = np.where(blank_raster_reduction > composite_raster_reduction, blank_raster_reduction, composite_raster_reduction)
        
        candidate_raster_coverage = candidates.candidate_data[raster_number]['coverage']
        blank_raster_coverage = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
        blank_raster_coverage[window.row_off:window.row_off + window.height, window.col_off:window.col_off + window.width] = candidate_raster_coverage
        composite_raster_coverage = np.where(blank_raster_coverage > composite_raster_coverage, blank_raster_coverage, composite_raster_coverage)
     
    result_raster_reduction = composite_raster_reduction * dwellings.main_data
    total_sum_reduction = np.sum(result_raster_reduction)
    
    result_raster_coverage = composite_raster_coverage * dwellings.main_data
    total_sum_coverage = np.sum(result_raster_coverage)
    
    result_raster_fairness = composite_raster_coverage * dwellings.isolation_data
    total_sum_fairness = np.sum(result_raster_fairness)
    
        
    return total_sum_reduction, total_sum_coverage, total_sum_fairness

def process_raster_for_visulisation(candidates, dwellings, selected_raster_numbers):
    # Load main raster extent and create blank raster
    composite_raster_reduction = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
    composite_raster_coverage = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
    
    # Iterate through selected raster numbers
    for raster_number in selected_raster_numbers:
        window = candidates.candidate_data[raster_number]['window']
        candidate_raster_reduction = candidates.candidate_data[raster_number]['reduction']
        blank_raster_reduction = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
        blank_raster_reduction[window.row_off:window.row_off + window.height, window.col_off:window.col_off + window.width] = candidate_raster_reduction
        
        composite_raster_reduction = np.where(blank_raster_reduction > composite_raster_reduction, blank_raster_reduction, composite_raster_reduction)
        
        candidate_raster_coverage = candidates.candidate_data[raster_number]['coverage']
        blank_raster_coverage = create_blank_raster(dwellings.main_extent, dwellings.main_transform, dwellings.main_width, dwellings.main_height)
        blank_raster_coverage[window.row_off:window.row_off + window.height, window.col_off:window.col_off + window.width] = candidate_raster_coverage
        composite_raster_coverage = np.where(blank_raster_coverage > composite_raster_coverage, blank_raster_coverage, composite_raster_coverage)
     
    result_raster_reduction = composite_raster_reduction * dwellings.main_data
    total_sum_reduction = np.sum(result_raster_reduction)
    
    result_raster_coverage = composite_raster_coverage * dwellings.main_data
    total_sum_coverage = np.sum(result_raster_coverage)
    
    result_raster_fairness = composite_raster_coverage * dwellings.isolation_data
    total_sum_fairness = np.sum(result_raster_fairness)
    
        
    return [total_sum_reduction, total_sum_coverage, total_sum_fairness], [result_raster_reduction, result_raster_coverage, total_sum_fairness]

