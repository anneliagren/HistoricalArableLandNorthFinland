#This script removes the class 0 (graphics) from the raster files and replaces it with NoData value.
import os
import glob
from osgeo import gdal
import numpy as np
import time

# Start time measurement
start_time = time.time()

input_raster_path  = '/workspace/data/AllMaps/PredictionArableFin/'

tiff_files = glob.glob(os.path.join(input_raster_path, '*.tif'))

# Check if raster files are found
if not tiff_files:
    print("No raster files found in the specified directory:", input_raster_path)
    exit()

# Specify the output directory
output_dir = '/workspace/data/AllMaps/PredictionArableFin/Nodata/'

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Loop over all raster files
for tiff_file in tiff_files:
    output_filename = os.path.basename(tiff_file)
    output_path = os.path.join(output_dir, output_filename)

    # Open the input raster file
    ds = gdal.Open(tiff_file)
    band = ds.GetRasterBand(1)

    # Read the raster data
    raster_data = band.ReadAsArray()

    # Convert class 2 to NoData
    nodata_value = 99  # Define your NoData value
    raster_data[(raster_data == 2)] = nodata_value

    # Create the output raster file
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_path, ds.RasterXSize, ds.RasterYSize, 1, band.DataType)
    out_band = out_ds.GetRasterBand(1)

    # Write the updated raster data to the output file
    out_band.WriteArray(raster_data)

    # Set the NoData value
    out_band.SetNoDataValue(band.GetNoDataValue())

    # Copy the georeferencing information
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())

    # Close the datasets
    ds = None
    out_ds = None

print("Processing completed.")
# End time measurement
end_time = time.time()
elapsed_time = end_time - start_time
print(f'Total execution time: {elapsed_time:.2f} seconds')