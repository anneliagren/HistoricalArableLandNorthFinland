import os
import numpy as np
from osgeo import gdal_array
import rasterio as rio
import pandas as pd
import xgboost as xgb
import time

# Start time measurement
start_time = time.time()

# Load the trained XGBoost model
model_file_path = '/workspace/data/XGBModelNew/xgboost_modelFin.json'
xgboost_modelFin = xgb.Booster()
xgboost_modelFin.load_model(model_file_path)

# Set the base directory
base_dir = '/workspace/data/AllMaps/ForPredictions/decompressed/'
output_dir = '/workspace/data/AllMaps/PredictionArableFin/'

# Define the correct order of bands. The order of features in the DMatrix used during training is what the model expects during prediction.
correct_order = ['Red', 'Green', 'Blue', 'B_G', 'B_R', 'G_R', 'Intensity', 'Hue', 'Saturation', 'MinFG3']

# Include these folders:
required_folders = ['B_G', 'B_R', 'Blue', 'G_R', 'Green', 'Hue', 'Intensity', 'MinFG3', 'Red', 'Saturation']

# Collect subfolder names
subfolder_names = [name for name in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, name)) and name in required_folders]
print(f"Subfolder names: {subfolder_names}")

# Ensure output folders exist
os.makedirs(output_dir, exist_ok=True)

# Iterate over the files in the original raster composite folder
for original_tif_name in os.listdir(base_dir):
    if original_tif_name.endswith('.tif'):
        output_file = os.path.join(output_dir, original_tif_name)
        
        # Check if the output file already exists
        if os.path.exists(output_file):
            print(f"Output file {output_file} already exists. Skipping {original_tif_name}.")
            continue
        
        print(f"Processing file: {original_tif_name}")
        bands_list = []
        original_tif_path = os.path.join(base_dir, original_tif_name)
        
        # Get the size of the TIFF file
        with rio.open(original_tif_path) as src:
            tif_height, tif_width = src.height, src.width
        
        no_data_mask = None
        
        for band_name in correct_order:
            subfolder_path = os.path.join(base_dir, band_name)
            subfolder_file_path = os.path.join(subfolder_path, original_tif_name)
            if os.path.exists(subfolder_file_path):
                try:
                    print(f"Loading band from: {subfolder_file_path}")
                    band = gdal_array.LoadFile(subfolder_file_path)
                    bands_list.append(band)
                    
                    # Update the no_data_mask
                    if no_data_mask is None:
                        no_data_mask = (band == -32768)
                    else:
                        no_data_mask = no_data_mask | (band == -32768)
                except ValueError as e:
                    print(f"Error loading band from {subfolder_file_path}: {e}")
                    continue
            else:
                print(f"Warning: {subfolder_file_path} does not exist.")
        
        # Check if we have the correct number of bands
        if len(bands_list) != 10:
            print(f"Error: Expected 10 bands, but found {len(bands_list)} for file {original_tif_name}. Skipping this file.")
            continue
        
        # Make list into array
        bands_list = np.array(bands_list)
        # Reshape the array to match the input format during training
        bands_list_reshape = bands_list.reshape(10, tif_height * tif_width).T

        # Create a DataFrame for prediction
        xgb_data = pd.DataFrame(bands_list_reshape, columns=correct_order)

        # Make a DMatrix
        d_data = xgb.DMatrix(xgb_data, feature_names=correct_order)

        # Make predictions
        predictions = xgboost_modelFin.predict(d_data)
        pred = predictions.reshape(tif_height, tif_width)

        # Apply the no_data_mask to the predictions
        if no_data_mask is not None:
            pred[no_data_mask] = -32768

        # Save predictions to a new raster file
        with rio.open(original_tif_path) as reference_raster:
            profile = reference_raster.profile
            profile.update(dtype=rio.int16, count=1, nodata=-32768)

        with rio.open(output_file, 'w', **profile) as dst:
            dst.write(pred, 1)
            print(f'Done processing {original_tif_name}')

# End time measurement
end_time = time.time()
elapsed_time = end_time - start_time
print(f'Total execution time: {elapsed_time:.2f} seconds')