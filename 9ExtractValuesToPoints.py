import numpy as np
import os
import pandas as pd
import geopandas as gpd
import rasterio as rio
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import pyogrio

"""
This script extracts raster values at specific point locations from raster tiles contained in all subfolders in a folder and 
saves the results into individual CSV files. Finally, it concatenates all these CSV files into 
a single CSV file.

Usage:
- This script is useful for extracting raster data for specific point locations and then combining these extracted values into one comprehensive dataset.
"""

# Define the root directory containing subfolders with raster tiles
raster_folder = '/workspace/data/AllMaps/ForPredictions/decompressed/'

# Define the folder containing point shapefiles
shapefile_folder = '/workspace/data/TrainTestPoints/ClippedPoints/'

# Define the folder to save the output CSVs
output_folder = '/workspace/data/TrainTestPoints/ExtractedValues/'

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Find all shapefiles in the folder
allpoints = glob.glob(os.path.join(shapefile_folder, '*.shp'))

# Initialize an empty DataFrame to accumulate all data
all_data = pd.DataFrame()

# List to keep track of missing raster files
missing_files = []

def process_shapefile(point, point_idx, total_points):
    # Load the shapefile as a GeoDataFrame using pyogrio
    pts = gpd.read_file(point, engine='pyogrio')
    
    # Extract the name of the shapefile (without extension) to match it with the raster tile
    pts_name = os.path.splitext(os.path.basename(point))[0]
    print(f'Reading point tile number {point_idx}/{total_points}: {pts_name}')
    
    # Print the columns of the shapefile for debugging
    print(f"Columns in {point}: {pts.columns}")
    
    # Check if the required columns exist
    if 'X' not in pts.columns or 'Y' not in pts.columns:
        print(f"Columns 'X' and 'Y' not found in {point}. Skipping.")
        return pd.DataFrame(), []
    
    # Create a list of coordinate pairs from the 'X' and 'Y' columns
    coords = [(x, y) for x, y in zip(pts.X, pts.Y)]
    
    # Initialize a DataFrame to store the extracted values for the current shapefile
    extracted_values = pd.DataFrame(coords, columns=['X', 'Y'])
    
    # Extract values from "Class" and "Id" columns if they exist
    if 'Class' in pts.columns:
        extracted_values['Class'] = pts['Class']
    if 'Id' in pts.columns:
        extracted_values['Id'] = pts['Id']
    
    # Add the filename of the shapefile to the DataFrame
    extracted_values['Shapefile'] = pts_name
    
    # List to keep track of missing raster files for this shapefile
    local_missing_files = []
    
    # Traverse through each subfolder inside the raster folder
    for subdir, _, _ in os.walk(raster_folder):
        # Extract the subfolder name
        subfolder_name = os.path.basename(subdir)
        
        # Look for the corresponding raster file in the subfolder
        raster_file = os.path.join(subdir, f'{pts_name}.tif')
        
        # Check if the corresponding raster tile exists in the subfolder
        if os.path.exists(raster_file):
            print(f'Found corresponding raster: {raster_file} in subfolder: {subfolder_name}')
            
            # Open the corresponding raster file (which contains only one band)
            with rio.open(raster_file) as src:
                # Extract raster values at the specified coordinates
                values = []
                for coord in coords:
                    try:
                        value = next(src.sample([coord]))[0]
                    except StopIteration:
                        value = np.nan
                    values.append(value)
                extracted_values[subfolder_name] = values
                print(f'Raster values from subfolder {subfolder_name} attached for {pts_name}!')
        else:
            # If the raster file does not exist, fill with NaN and log the missing file
            extracted_values[subfolder_name] = np.nan
            local_missing_files.append(raster_file)
            print(f'Raster file {raster_file} not found. Filling with NaN.')
    
    # Print the extracted values for debugging
    print(f"Extracted values for {pts_name}:")
    print(extracted_values)
    
    return extracted_values, local_missing_files

# Use ThreadPoolExecutor to process shapefiles in parallel
with ThreadPoolExecutor(max_workers=60) as executor:
    futures = [executor.submit(process_shapefile, point, idx, len(allpoints)) for idx, point in enumerate(allpoints, start=1)]
    
    for future in as_completed(futures):
        extracted_values, local_missing_files = future.result()
        all_data = pd.concat([all_data, extracted_values], ignore_index=True)
        missing_files.extend(local_missing_files)

# Print the accumulated DataFrame for debugging
print("Accumulated DataFrame:")
print(all_data)

# Save the accumulated DataFrame to a single CSV file
output_csv = os.path.join(output_folder, 'compiled_extracted_values_Fin.csv')
all_data.to_csv(output_csv, index=False)
print(f'Compiled CSV saved at: {output_csv}')

# Print summary of missing files
if missing_files:
    print("\nSummary of missing raster files:")
    for missing_file in missing_files:
        print(missing_file)
else:
    print("\nNo missing raster files.")