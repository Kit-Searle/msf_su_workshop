#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 04:12:27 2024

@author: ksearle
"""
import json
import numpy as np
import networkx as nx
from scipy.spatial import Voronoi
import rasterio
from rasterio.windows import Window
import matplotlib.pyplot as plt
import contextily as ctx  # For adding basemaps to geographic data plots


class Candidates:
    """
    Manages candidate locations for the multi resolution NSGA II problem.

    This class loads candidate site locations from a geojson file, stores them, 
    and facilitates operations like retrieving candidate data and neighboring locations.
    """

    def __init__(self,data_file):
        """
        Initializes the CandidateManager with a specified candidate location file.

        Attributes:
            candidates_location_file (str): The file path to the geojson file 
                                            containing candidate locations.
            candidate_locations (dict): A dictionary mapping candidate IDs to 
                                        their coordinates (loaded from file).
            candidates (dict or None): Stores selected candidates after filtering 
                                       by a specific resolution (initialized as None).
            neighbours (dict or None): Stores neighboring locations around each 
                                       candidate, based on a proximity criterion 
                                       (initialized as None).
        """
        
        
        self.candidates_location_file = data_file / 'candidates.geojson'
        self.all_candidates = self.load_candidate_locations()
        self.main_raster_path = data_file / "dwellings_count_utm_clipped.tif"
        self.data_file = data_file
        self.candidate_data = dict()

    def load_candidate_locations(self):
        """
        Loads candidate locations from a geojson file and organizes them by ID.

        The function reads data from the specified geojson file, extracts each candidate's 
        unique ID and coordinates, and stores them in a dictionary.

        Returns:
            dict: A dictionary where keys are candidate IDs and values are coordinates 
                  in the form of (longitude, latitude) tuples.
        """
        with open(self.candidates_location_file) as f:
            data = json.load(f)
        # Create a dictionary of candidate locations with ID as the key and coordinates as values
        return {feature['properties']['new_id']: feature['geometry']['coordinates'] for feature in data['features']}
    
    def get_voronoi(self):
        """
        Constructs a Voronoi diagram from candidate coordinates and 
        builds an adjacency graph where edges connect neighboring sites.
        """
    
        # --- STEP 1: Extract candidate IDs and coordinates ---
        # 'self.candidates' is assumed to be a dictionary:
        #   key   = candidate ID
        #   value = (x, y) coordinate
        ids = list(self.all_candidates.keys())
        coords = np.array(list(self.all_candidates.values()))
    
        # --- STEP 2: Compute Voronoi diagram ---
        # Each candidate location becomes a Voronoi seed point.
        vor = Voronoi(coords)
    
        # --- STEP 3: Initialize adjacency graph ---
        # Use a NetworkX graph to represent neighbor relationships
        # between candidate sites.
        self.G = nx.Graph()
        self.G.add_nodes_from(ids)  # Add all candidates as graph nodes
    
        # --- STEP 4: Add edges based on Voronoi adjacency ---
        # ridge_points gives pairs of sites whose Voronoi cells share a border.
        for p1, p2 in vor.ridge_points:
            id1, id2 = ids[p1], ids[p2]  # Map Voronoi indices back to candidate IDs
            self.G.add_edge(id1, id2)    # Connect candidates that are neighbors
        

    
    def get_nearest_neighbours(self, location, dist):
        """
        Find nearest neighbors of a given location using the Voronoi adjacency graph.
        Neighboring sites are considered if they lie within a distance threshold.
    
        Args:
            location (int/str): Candidate ID for which neighbors are being searched.
            dist (float): Multiplier for the minimum neighbor distance 
                          (controls neighborhood radius).
    
        Returns:
            dict: Mapping of neighbor IDs to their coordinates.
        """
    
        # --- STEP 1: Setup containers ---
        all_neighbours = {}   # Dictionary to store neighbor IDs and coordinates
        visited = set()       # Track already-visited nodes to avoid cycles
        queue = [location]    # BFS queue initialized with the starting location
    
        # --- STEP 2: Define distance threshold ---
        # Compute the minimum Euclidean distance between the chosen location
        # and each of its direct Voronoi neighbors.
        # Multiply by 'dist' to scale the allowable neighborhood radius.
        dist_threshold = dist * min(
            np.linalg.norm(
                np.array(self.all_candidates[location]) - np.array(self.all_candidates[neighbour])
            )
            for neighbour in self.G.neighbors(location)
        )
    
        # --- STEP 3: Breadth-First Search (BFS) through Voronoi neighbors ---
        while queue:
            current = queue.pop(0)  # Dequeue next node
            if current not in visited:
                visited.add(current)  # Mark as visited
    
                # Explore all Voronoi neighbors of the current node
                for neighbour in self.G.neighbors(current):
                    if neighbour not in visited:
                        # Compute Euclidean distance from original 'location' to this neighbor
                        edge_dist = np.linalg.norm(
                            np.array(self.all_candidates[location]) - np.array(self.all_candidates[neighbour])
                        )
    
                        # If the neighbor lies within the distance threshold, add it
                        if edge_dist <= dist_threshold:
                            queue.append(neighbour)  # Enqueue for further exploration
                            all_neighbours[neighbour] = self.all_candidates[neighbour]

        # --- STEP 4: Return dictionary of valid neighbors ---
        return all_neighbours

                            
   
    def plot_graph(self):
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw edges
        nx.draw_networkx_edges(self.G, pos=self.all_candidates, edge_color='gray', width=0.5)


        # Draw nodes
        nx.draw_networkx_nodes(
            self.G,
            pos=self.all_candidates,
            node_color='skyblue',
            node_size=2.5
        )

        # Add node indices inside circles
        # labels = {n: n for n in G.nodes()}
        # nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=8, font_color='black')
        
        ctx.add_basemap(ax, crs="EPSG:32738")
        
        plt.axis('off')
        plt.show()
    
    
            
    def load_data(self): 
        
        with rasterio.open(self.main_raster_path) as src:
            main_extent,  main_transform,  main_width,  main_height = src.bounds, src.transform, src.width, src.height
        
        for candidate in self.all_candidates:
                with rasterio.open(self.data_file / 'v_i' / f'dry_walk_site_{candidate}.tif') as src:
                    # Align small raster extent with main raster extent
                    window = self.align_raster_to_main(src, main_transform, main_width, main_height)
                    reduction = src.read(1, window=Window(0, 0, window.width, window.height))
                    reduction = np.where(reduction < 0, 0, reduction)
                    reduction = reduction/1000
                    
                
                with rasterio.open(self.data_file / 'v_b' / f'dry_walk_site_{candidate}.tif') as src:
                    # Align small raster extent with main raster extent
                    
                    coverage = src.read(1, window=Window(0, 0, window.width, window.height))
                    coverage = np.where(coverage < 0, 0, coverage)
                    
                with rasterio.open(self.data_file / 'v_t' / f'dry_walk_site_{candidate}.tif') as src:
                    # Align small raster extent with main raster extent
                    
                    time_taken = src.read(1, window=Window(0, 0, window.width, window.height))
                    time_taken = np.where(time_taken < 0, 0, time_taken)
                    time_taken = time_taken/1000
                    
                self.candidate_data[candidate] = {'window': window, 'reduction': reduction, 'coverage': coverage, 'time': time_taken }
        

    def align_raster_to_main(self,small_raster, main_transform, main_width, main_height):
        small_bounds = small_raster.bounds
        col_start = int((small_bounds.left - main_transform[2]) / main_transform[0])
        row_start = int((small_bounds.top - main_transform[5]) / main_transform[4])
        
        col_stop = col_start + small_raster.width
        row_stop = row_start + small_raster.height
        
        # Ensure indices are within main raster bounds
        col_start = max(col_start, 0)
        row_start = max(row_start, 0)
        col_stop = min(col_stop, main_width)
        row_stop = min(row_stop, main_height)
        
        
        window = Window.from_slices((row_start, row_stop), (col_start, col_stop))
        return window

