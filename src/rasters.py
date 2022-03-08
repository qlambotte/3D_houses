import rasterio.plot as rplt
import numpy as np
import rasterio.mask
import rasterio
import glob
from rasterio.merge import merge
from shapely.geometry import Polygon


def crop_rasters(dsm: str, dtm: str, shapes: list[Polygon], name: str) -> None:
    with rasterio.open(dsm) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    out_meta.update(
        {
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        }
    )
    with rasterio.open(
        f"./data/{name}_dsm_croped.tiff", "w", **out_meta
    ) as dest:
        dest.write(out_image)
    with rasterio.open(dtm) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta
    out_meta.update(
        {
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        }
    )
    with rasterio.open(
        f"./data/{name}_dtm_croped.tiff", "w", **out_meta
    ) as dest:
        dest.write(out_image)


def do_merge(list_files: list[str]):
    list_opened_files = []
    for raster in list_files:
        src = rasterio.open(raster)
        list_opened_files.append(src)
    out_meta = src.meta.copy()
    mosaic, out_trans = merge(list_opened_files)
    out_meta.update(
        {
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
        }
    )
    return mosaic, out_trans, out_meta


def merge_rasters(name: str) -> None:
    for d in ["dsm", "dtm"]:
        list_files = glob.glob(f"./data/*_{d}_croped.tiff")
        mosaic, out_trans, out_meta = do_merge(list_files)
        with rasterio.open(
            f"./data/{name}_{d}_croped.tiff", "w", **out_meta
        ) as file:
            file.write(mosaic)


def chm(dtm: str, dsm: str, name: str) -> np.ndarray:
    with rasterio.open(dtm, "r") as file:
        dtm = file.read(1)
        profile_dtm = file.profile
    with rasterio.open(dsm, "r") as file:
        dsm = file.read(1)
    chm = dsm - dtm
    return chm
