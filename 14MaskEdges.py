import os
import numpy as np
import rasterio
from rasterio.enums import Resampling

# Define the directory containing the TIFF and mask files
tiff_dir = '/workspace/data/AllMaps/PredictionArableFin/Nographic'
output_dir = '/workspace/data/AllMaps/PredictionArableFin/Nographic/Processed'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get the list of all TIFF files and corresponding mask files
tiff_files = [os.path.join(tiff_dir, f) for f in os.listdir(tiff_dir) if f.endswith('.tif')]
mask_files = [os.path.join(tiff_dir, f"{os.path.splitext(f)[0]}.tif.msk") for f in os.listdir(tiff_dir) if f.endswith('.tif')]

print("Processing TIFF and mask files...")

for tiff_file, mask_file in zip(tiff_files, mask_files):
    try:
        print(f"Processing: {tiff_file} with mask: {mask_file}")
        if not os.path.exists(mask_file):
            print(f"Mask file does not exist: {mask_file}. Skipping...")
            continue

        # Open the TIFF file
        with rasterio.open(tiff_file) as src:
            tiff_data = src.read(1, masked=True)  # Read the first band
            tiff_meta = src.meta.copy()

        # Open the mask file
        with rasterio.open(mask_file) as mask_src:
            mask_data = mask_src.read(1)  # Read the first band

        # Set TIFF cells to nodata where the mask is 0
        tiff_data[mask_data == 0] = tiff_meta['nodata']

        # Update metadata for the output file
        tiff_meta.update({
            "driver": "GTiff",
            "dtype": tiff_data.dtype,
            "nodata": tiff_meta['nodata']
        })

        # Write the modified TIFF to the output directory
        output_file = os.path.join(output_dir, os.path.basename(tiff_file))
        with rasterio.open(output_file, "w", **tiff_meta) as dst:
            dst.write(tiff_data, 1)

        print(f"Saved processed file to: {output_file}")

    except Exception as e:
        print(f"Error processing {tiff_file} with mask {mask_file}: {e}")

print("Processing complete.")