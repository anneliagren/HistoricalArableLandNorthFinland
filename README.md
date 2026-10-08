# Historical Arable Land in Northern Finland

This repository contains the scripts required to automatically detect arable land from high‑resolution (1:20,000) scanned historical maps, specifically the Finnish Basemaps produced between **1947 and 1979**.

A machine learning model based on **Extreme Gradient Boosting (XGBoost)** was developed to identify arable land.  
The model achieved exceptional performance, with a **Cohen’s Kappa** and **Matthews Correlation Coefficient** of **0.992**.

Class‑wise performance for arable land detection was nearly perfect, with:
- **Recall:** 1.000  
- **Precision:** 0.998  
- **F1 score:** 0.995  

This historical dataset enables detailed, field‑level analyses of arable land use in the **Finnish Arctic region** and provides valuable insights into long‑term land‑use dynamics.

---

## Data availability

A map of historical arable land for **Northern Finland** is publicly available at:

🔗 https://etsin.fairdata.fi/dataset/00f52e65-1ece-4c52-a68d-21fb0021d883

## Overview Map 


The historical paper map series was printed between 1949 and 1998 and covers a total of 11,000 maps. This study focus on 938 map tiles from northern Finland. The dataset is a composite of the oldest available map for each site. In the study region the maps were produced between 1949-1979, so the datset spans a composite covering 40 decades. For interpreting the details of the dataset, a map overview file is found in "OverviewShapeFile.shp". The shapefile contains the boundaries of each map tile. Furthermore, in the attribute table the column 'file name' contains the filename of the original downloaded maps and the column 'year' indicate the print year of the map tile.
<img width="226" height="410" alt="image" src="https://github.com/user-attachments/assets/158f0e6e-aff4-426e-b292-d82151f7d5fd" />

---

## Running the workflow for the rest of Finland

To apply this workflow to the rest of Finland:

1. Download the scanned paper maps from  
   🔗 https://paituli.csc.fi/download.html

2. Download the code provided in this repository.

3. Run the scripts in the **ZIP code folder** in the numerical order in which they are named.

4. **Update all file paths** in the scripts to match your local directory structure.

---

## Related publication

A full data descriptor will be published in *Scientific Data*.  
Once the article is accepted, this section will be updated with a direct link to the publication.
