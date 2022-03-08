"""
This module collects data from a parcel given an adress.
"""
from shapely.geometry import Point, Polygon
from utilities import bbox_enlarged, square_envelope
import requests
import json


def get_info_parcel(
    street: str, commune: str, postcode: int, number: str
) -> json:
    url = "https://api.basisregisters.vlaanderen.be/v1/adresmatch?"
    r = requests.get(
        url,
        params={
            "gemeentenaam": commune,
            "straatnaam": street,
            "huisnummer": number,
            "postcode": postcode,
        },
    )
    return r.json()


def get_object_details(parcel: json) -> dict:
    objects = parcel["adresMatches"][0]["adresseerbareObjecten"]
    details = {
        "id_adress": parcel["adresMatches"][0]["identificator"]["objectId"]
    }
    for obj in objects:
        if obj["objectType"] == "gebouweenheid":
            intermediate = requests.get(obj["detail"]).json()
            geometry_url = intermediate["gebouw"]["detail"]
            geometry = requests.get(geometry_url).json()["geometriePolygoon"]
            details[
                f"building_{intermediate['identificator']['objectId']}"
            ] = Polygon(geometry["polygon"]["coordinates"][0])
        if obj["objectType"] == "perceel":
            capakey = obj["objectId"].replace("-", "/")
            url = (
                "https://geoservices.informatievlaanderen.be/"
                f"capakey/api/v2/parcel/{capakey}/"
            )
            r = requests.get(url).json()
            bbox_coordinates = json.loads(r["geometry"]["boundingBox"])
            details["bbox"] = Polygon(bbox_coordinates["coordinates"][0])
    return details


def get_map_parcel(parcel_details: dict, frac: float=0.3) -> str:
    bbox = parcel_details["bbox"].bounds
    x_min, y_min, x_max, y_max = square_envelope(bbox_enlarged(bbox, frac=frac))
    url = (
        "https://geoservices.informatievlaanderen.be/raadpleegdiensten/"
        "GRB-basiskaart/wms?service=WMS&request=GETMAP&WIDTH=1034"
        "&HEIGHT=1024&LAYERS=GRB_BSK&FORMAT=image/geotiff"
        f"&SRS=EPSG:31370&BBOX={x_min},{y_min},{x_max},{y_max}"
    )
    r = requests.get(url)
    name = parcel_details["id_adress"]
    with open(f"./data/{name}.tiff", "wb") as file:
        file.write(r.content)
    return f"./data/{name}.tiff"
