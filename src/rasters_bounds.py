"""
This module extracts the bounds of the DRM and DTM raster files from de
Flemish region, found in
 - (DSM) http://www.geopunt.be/download?container=dhm-vlaanderen-ii-dsm-raster-1m&title=Digitaal%20Hoogtemodel%20Vlaanderen%20II,%20DSM,%20raster,%201m
 - (DTM) http://www.geopunt.be/download?container=dhm-vlaanderen-ii-dtm-raster-1m&title=Digitaal%20Hoogtemodel%20Vlaanderen%20II,%20DTM,%20raster,%201m

The data is extracted from:  https://www.geopunt.be/download?container=kaartbladversnijding-ngi-numeriek&title=Kaartbladversnijdingen
"""

import geopandas as gp

gf = gp.read_file("./data/Kbl/Kbl.shp")

squares = gf[["UIDN", "CODE", "geometry"]]

if __name__ == "__main__":
    squares.to_csv("./data/rasters_limits.csv")
