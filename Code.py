import arcpy
import pandas as pd
import math


project_folder = r"C:\Users\ajots\Downloads\Hosipital Project"
gdb            = r"C:\Users\ajots\OneDrive\Documents\ArcGIS\Projects\PeelHosipitalsProject\PeelHosipitalsProject.gdb"
hospitals_csv  = project_folder + r"\hosipitals_peel.csv"
shapefile      = project_folder + r"\lda_000b21a_e.shp"

# Loading hospital points into the geodatabase
print("Please wait while hospital points load ...")
arcpy.env.workspace = gdb
if arcpy.Exists("hospitals_pts"):
    arcpy.Delete_management("hospitals_pts")
arcpy.management.XYTableToPoint(
    in_table          = hospitals_csv,
    out_feature_class = gdb + r"\hospitals_pts",
    x_field           = "lon",
    y_field           = "lat",
    coordinate_system = arcpy.SpatialReference(4326)
)
print("Hospital points loading done.")

# Reading the shapefile using arcpy
print("DA Shapefile reading ongoing ...")
arcpy.env.workspace = project_folder
fields = ["DAUID", "SHAPE@"]
rows = []
with arcpy.da.SearchCursor(shapefile, fields) as cursor:
    for row in cursor:
        if str(row[0]).startswith("3521"):
            centroid = row[1].centroid
            rows.append({
                "DAUID":      str(row[0]),
                "centroid_x": centroid.X,
                "centroid_y": centroid.Y
            })
da = pd.DataFrame(rows)
print(f"Found {len(da)} Peel Region DAs")

# Converting google coordinates for the hospitals into the same number system used by the shapefile
print("Converting hospital coordinates")
hospitals_gps = {
    # Coordinates found from google maps
    "Brampton Civic Hospital": (43.747414876679315, -79.74347844499333),
    "Peel Memorial Centre":    (43.69042362799345,  -79.75104787383135),
    "Credit Valley Hospital":  (43.55906474365877,  -79.70330430267245),
    "Mississauga Hospital":    (43.57188532701062,  -79.60761628917865)
}
sr_shapefile = arcpy.Describe(shapefile).spatialReference
sr_gps       = arcpy.SpatialReference(4326)
hospitals_projected = {}
for name, (lat, lon) in hospitals_gps.items():
    pt_geom  = arcpy.PointGeometry(arcpy.Point(lon, lat), sr_gps)
    pt_proj  = pt_geom.projectAs(sr_shapefile)
    hospitals_projected[name] = (pt_proj.firstPoint.X, pt_proj.firstPoint.Y)
    print(f"  {name}: projected successfully")

# Finding which hospital is closest to each Dissemination  Area 
print("Finding nearest hospital for each DA...")
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

da["nearest_hospital"] = None
for idx, row in da.iterrows():
    min_dist = float("inf")
    nearest  = None
    for name, (hx, hy) in hospitals_projected.items():
        dist = distance(row["centroid_x"], row["centroid_y"], hx, hy)
        if dist < min_dist:
            min_dist = dist
            nearest  = name
    da.at[idx, "nearest_hospital"] = nearest
print(da["nearest_hospital"].value_counts())

# Calculate how much of the population is served by each hospital
print("\nCalculating population served...")
city_pop  = {"Brampton": 656480, "Mississauga": 717961, "Caledon": 76581}
total_pop = sum(city_pop.values())
pop_per_da = total_pop / len(da)
result = da["nearest_hospital"].value_counts().reset_index()
result.columns = ["hospital", "da_count"]
result["est_population"] = (result["da_count"] * pop_per_da).astype(int)
print("\n--- Population Served Per Hospital ---")
for _, row in result.iterrows():
    print(f"{row['hospital']}: {row['da_count']} DAs → ~{row['est_population']:,} people")

#  Saving the DA and Result tables to the CSV to portray final results 
print("\nSaving results...")
da[["DAUID", "nearest_hospital"]].to_csv(
    project_folder + r"\da_hospital_assignment.csv", index=False)
result.to_csv(project_folder + r"\catchment_results.csv", index=False)
print("CSVs saved!")

# Filtering the huge Canada layer and making a new Peel Region only layer and adding to geodatabase
print("Loading Peel DA layer into geodatabase...")
if arcpy.Exists(gdb + r"\peel_DA_hospitals"):
    arcpy.Delete_management(gdb + r"\peel_DA_hospitals")
arcpy.management.MakeFeatureLayer(
    gdb + r"\lda_000b21a_e", "peel_layer", "DAUID LIKE '3521%'")
arcpy.conversion.FeatureClassToFeatureClass("peel_layer", gdb, "peel_DA_hospitals")
print("Peel DA layer created!")

# Using a lookup dict to assign an hospital to each DA for the final results to show the split
print("Writing hospital assignments to layer...")
lookup = dict(zip(da["DAUID"], da["nearest_hospital"]))
with arcpy.da.UpdateCursor(gdb + r"\peel_DA_hospitals", ["DAUID", "nearest_hospital"]) as cursor:
    for row in cursor:
        if str(row[0]) in lookup:
            row[1] = lookup[str(row[0])]
            cursor.updateRow(row)
print("Done! Open ArcGIS Pro and symbolize peel_DA_hospitals by nearest_hospital field.")