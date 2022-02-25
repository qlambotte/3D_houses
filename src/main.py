import numpy as np
import rasterio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import download_plotlyjs, plot
import parcel
import utilities as u
import rasters
from skimage import io
import plotly.express as px
#from PIL import Image

def plot3d(chm, parcel_image, adress):
    fig = make_subplots(rows=1, cols=2,
                        specs=[[{"type": "image"},{"type": "surface"}]])

    fig.add_trace(
        go.Surface(z=chm),
        row=1, col=2
    )
    fig.update_layout(title=f'3D rendering of {adress}', title_x=0.5,
                      scene = dict(
                          xaxis_title='x (m)',
                          yaxis_title='y (m)',
                          zaxis_title='Height (m)',
                          yaxis_autorange="reversed",
                          aspectmode='data'),
                      font=dict(
                          family="Courier New, monospace",
                          size=18)
                      )
    fig.add_trace(
        go.Image(z=io.imread(parcel_image)),
        row=1, col=1
    )
    fig.update_layout(yaxis={'visible': False, 'showticklabels': False},
                      xaxis={'visible': False, 'showticklabels': False})
    plot(fig)
def path_of_id(id, type_):
    if int(id) < 10:
        id = f"0{id}"
    name = f"DHMVII{type_.upper()}RAS1m_k{id}"
    path = (
        f"zip://./../../data_rasters/{type_}/"
        f"{name}.zip!"
        f"GeoTIFF/{name}.tif"
    )
    return path

def adress_from_input():
    print(
        "Welcome! This program will give you a 3D rendering of a building,\n"
        "given an adress in Flanders, Belgium. You will be asked to enter\n"
        "successively the street namen the number, the postcode and"
        "the commune."
    )
    street = input("Please enter the street of the building "
                   "(ex.: Korenmarkt): "
                   )
    number = input("Now the number (ex.: 15): ")
    postcode = input("Now the postcode (ex: 9000): ")
    commune = input("Finally, the commune (ex: Gent): ")
    return street, number, postcode, commune
if __name__ == "__main__":
    street, number, postcode, commune = adress_from_input()
    if street == "":
        street = "Korenmarkt"
        number = 15
        postcode = 9000
        commune = "Gent"
    adress = f'{street} {number}, {postcode} {commune}'
    parcel_ = parcel.get_info_parcel(street, commune, postcode, number)
    parcel_details = parcel.get_object_details(parcel_)
    bbox = parcel_details["bbox"]
    rasters_info = u.rasters_of_bbox(bbox.bounds, "./data/Kbl/Kbl.shp",
                                     "geometry",
                                     "CODE")
    shapes = [bbox]
    for name, id in rasters_info.items():
        dsm = path_of_id(id, "dsm")
        dtm = path_of_id(id, "dtm")
        rasters.crop_rasters(dsm, dtm, shapes, name)
    if len(rasters_info) > 1:
        rasters.merge("all")
    shapes = [parcel_details[key] for key in parcel_details.keys() if "building" in key]
    rasters.crop_rasters("./data/all_dsm_croped.tiff",
                         "./data/all_dtm_croped.tiff",
                         shapes,
                         "all")
    chm = rasters.chm("./data/all_dtm_croped.tiff",
                      "./data/all_dsm_croped.tiff",
                      parcel_details['id_adress'])
    img = parcel.get_map_parcel(parcel_details)
    plot3d(chm, img, adress)
