import os
import subprocess

# Set the paths
vrt_file = "/workspace/data/AllMaps/PredictionArableFin/Nographic/Mosaics/composite.vrt"
basemap = "/workspace/data/FromAura20250203/Finnish_harmonized_CLC_20m_corine/CLC2018_harmonisoitu_20m.tif"
output_folder = "/workspace/data/AllMaps/PredictionArableFin/Nographic/Mosaics"
aggregated_output = os.path.join(output_folder, "ArableFin_aggregated_20m.tif")


# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Get the extent of the basemap
print("Fetching basemap information...")
basemap_info = subprocess.check_output(["gdalinfo", basemap], text=True)

# Extract the extent (Lower Left and Upper Right)
extent_lines = [line for line in basemap_info.splitlines() if "Lower Left" in line or "Upper Right" in line]
extent = []
for line in extent_lines:
    coords = line.split("(")[1].split(")")[0].split(",")
    extent.extend([coords[0].strip(), coords[1].strip()])

# Aggregate the VRT to 20m resolution using the basemap and reproject to EPSG:3067
print("Aggregating VRT to 20m resolution and reprojecting to EPSG:3067...")
subprocess.run([
    "gdalwarp",
    "-tr", "20", "20",  # Set target resolution to 20m
    "-r", "average",  # Use average resampling
    "-t_srs", "EPSG:3067",  # Reproject to EUREF FIN TM35FIN (EPSG:3067)
    "-te", extent[0], extent[1], extent[2], extent[3],  # Use the extent of the basemap
    vrt_file,
    aggregated_output
])

print(f"Aggregation complete. Output saved to {aggregated_output}.")


