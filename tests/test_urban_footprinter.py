import unittest

import numpy as np
import rasterio as rio
from shapely.geometry import base

import urban_footprinter as ufp


class Test(unittest.TestCase):
    def setUp(self):
        self.raster_filepath = 'notebooks/data/zurich.tif'
        with rio.open(self.raster_filepath) as src:
            self.raster_arr = src.read(1)
            self.res = src.res[0]  # only square pixels are supported
        self.kernel_radius = 500
        self.urban_threshold = .25
        self.urban_classes = list(range(8))

    def test_footprint_mask(self):
        # test two main input ways: raster filepath and ndarray
        urban_mask = ufp.urban_footprint_mask(self.raster_filepath,
                                              self.kernel_radius,
                                              self.urban_threshold,
                                              urban_classes=self.urban_classes)
        self.assertIsInstance(urban_mask, np.ndarray)

        urban_mask = ufp.urban_footprint_mask(self.raster_arr,
                                              self.kernel_radius,
                                              self.urban_threshold,
                                              urban_classes=self.urban_classes,
                                              res=self.res)
        self.assertIsInstance(urban_mask, np.ndarray)

        # test that providing a ndarray without the resolution raises a
        # ValueError
        self.assertRaises(ValueError, ufp.urban_footprint_mask,
                          self.raster_arr, self.kernel_radius,
                          self.urban_threshold,
                          urban_classes=self.urban_classes)

        # test that not providing urban classes raises a ValueError
        self.assertRaises(ValueError, ufp.urban_footprint_mask,
                          self.raster_filepath, self.kernel_radius,
                          self.urban_threshold)

        # test that getting more than the largest patch must return at least
        # the same number of pixels
        num_pixels = np.sum(urban_mask)
        self.assertGreaterEqual(
            np.sum(
                ufp.urban_footprint_mask(self.raster_filepath,
                                         self.kernel_radius,
                                         self.urban_threshold,
                                         urban_classes=self.urban_classes,
                                         largest_patch_only=False)),
            num_pixels)
        # test the same but for a positive buffer dist
        self.assertGreaterEqual(
            np.sum(
                ufp.urban_footprint_mask(self.raster_filepath,
                                         self.kernel_radius,
                                         self.urban_threshold,
                                         urban_classes=self.urban_classes,
                                         buffer_dist=1000)), num_pixels)

        # test that `urban_footprint_mask_shp` returns a shapely geometry
        urban_mask = ufp.urban_footprint_mask_shp(
            self.raster_filepath, self.kernel_radius, self.urban_threshold,
            urban_classes=self.urban_classes)
        self.assertIsInstance(urban_mask, base.BaseGeometry)