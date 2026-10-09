#!/bin/bash
# Unpack compressed tiff files
mkdir -p /workspace/data/AllMaps/ForPredictions/decompressed

for file in /workspace/data/AllMaps/ForPredictions/*.tif; do
    echo "Processing $file"
    gdal_translate -co COMPRESS=NONE "$file" "/workspace/data/AllMaps/ForPredictions/decompressed/$(basename $file)"
done