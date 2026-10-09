# Set the paths
output_folder="/workspace/data/AllMaps/PredictionArableFin/Nographic/Processed"
mosaics_folder="/workspace/data/AllMaps/PredictionArableFin/Nographic/Mosaics"


# Ensure the mosaics folder exists
mkdir -p "$mosaics_folder"

# Create a VRT file from all TIFFs in the subfolder
gdalbuildvrt "$mosaics_folder/composite.vrt" "$output_folder"/*.tif

