# Program Description

A GIS-based population catchment analysis tool built with Python and ArcGIS Pro 
that maps hospital service areas across Peel Region, Ontario and estimates the 
population served by each hospital.

## Project Overview
Peel Region has 4 major hospitals serving a population of over 1.4 million people.
This project uses dissemination area boundaries from Statistics Canada and hospital 
location data to determine which hospital is nearest to each neighbourhood and 
estimates the population each hospital is responsible for serving.

## Results
| Hospital | Neighbourhoods | Est. Population Served |
|---|---|---|
| Credit Valley Hospital | 458 | ~380,623 |
| Brampton Civic Hospital | 438 | ~364,002 |
| Peel Memorial Centre | 428 | ~355,691 |
| Mississauga Hospital | 422 | ~350,705 |

## Tools & Technologies
- Python 
- ArcGIS Pro (arcpy)
- pandas
- geopandas
- Statistics Canada 2021 Census Data
- OpenStreetMap via ArcGIS Living Atlas

## How It Works
1. Hospital locations geocoded from coordinates into ArcGIS feature layer
2. Dissemination area boundaries filtered to Peel Region (1,746 DAs)
3. Each DA centroid projected to match shapefile coordinate system
4. Nearest hospital calculated for each DA using Euclidean distance
5. Population apportioned proportionally across DAs
6. Results visualized as a choropleth map in ArcGIS Pro

## Data Sources
Download these files and place them in the project folder before running:

1. **DA Boundary Shapefile**
   https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/files-fichiers/lda_000b21a_e.zip

2. **Statistics Canada Census Profile 2021**
   https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm
   Select: Comprehensive download files → Ontario CSDs and DAs

## Files Included
- `Code.py` — main analysis script
- `hosipitals_peel.csv` — hospital coordinates
- `da_hospital_assignment.csv` — each DA and its nearest hospital
- `catchment_results.csv` — final population served per hospital
- `README.md` — this file

## How To Run
1. Download the data files above and place in the project folder
2. Update the file paths at the top of `Code.py` to match your machine
3. Open ArcGIS Pro and run via the Python window:
