import os
import rasterio
import numpy as np
import time
import whitebox

# Start WhiteboxTools
os.environ["WBT_LINUX"] = "MUSL"
os.environ["RUST_BACKTRACE"] = "full"  # Enable backtrace for detailed error information
whitebox.download_wbt(linux_musl=True, reset=True)
wbt = whitebox.WhiteboxTools()

# Record the start time of the script
start_time = time.time()

# Set input folder path
folder_path = '/workspace/data/AllMaps/ForPredictions/decompressed'

# Create output folders for each color band
output_red_folder = os.path.join(folder_path, 'Red')
output_green_folder = os.path.join(folder_path, 'Green')
output_blue_folder = os.path.join(folder_path, 'Blue')

# Ensure output folders exist
os.makedirs(output_red_folder, exist_ok=True)
os.makedirs(output_green_folder, exist_ok=True)
os.makedirs(output_blue_folder, exist_ok=True)

# Function to re-save TIFF with supported compression
def resave_with_supported_compression(input_path, output_path):
    with rasterio.open(input_path) as src:
        profile = src.profile
        profile.update(compress='lzw')
        with rasterio.open(output_path, 'w', **profile) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i), i)

# Iterate over the files in the folder
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    
    # Check if the file is a TIFF
    if file_name.endswith('.tif'):
        base_name = os.path.splitext(file_name)[0]

        # Construct the output file paths for each color band
        output_R = os.path.join(output_red_folder, f"{base_name}.tif")
        output_G = os.path.join(output_green_folder, f"{base_name}.tif")
        output_B = os.path.join(output_blue_folder, f"{base_name}.tif")

        # Temporary file path with supported compression
        temp_file_path = os.path.join(folder_path, f"temp_{file_name}")

        try:
            print(f"Processing {file_name}...")
            # Re-save the input file with supported compression
            resave_with_supported_compression(file_path, temp_file_path)

            # Run whiteboxtools split_colour_composite for each color band
            wbt.split_colour_composite(
                i=temp_file_path,
                red=output_R,
                green=output_G,
                blue=output_B
            )

            # Open the output files and replace zeros with ones
            for band_path in [output_R, output_G, output_B]:
                with rasterio.open(band_path, 'r+') as src:
                    band = src.read(1)
                    band[band == 0] = 1
                    src.write(band, 1)
                    print(f"Zeros replaced with ones in {band_path}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

        finally:
            # Remove the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

# Record the end time of the script
end_time = time.time()

# Calculate the total elapsed time
total_elapsed_time = end_time - start_time

# Print the total elapsed time
print(f"Total time for the script: {total_elapsed_time:.2f} seconds")
# Ensure the time log directory exists
time_log_dir = 'workspace/data/AllMaps/TimeAllMaps'
os.makedirs(time_log_dir, exist_ok=True)

# Save the time to a file
time_log_path = os.path.join(time_log_dir, '1RGBSplitTime.txt')
with open(time_log_path, 'a') as file:
    file.write(f"Script: {os.path.basename(__file__)}\n")
    file.write(f"Time: {total_elapsed_time:.2f} seconds\n")
    file.write("\n")