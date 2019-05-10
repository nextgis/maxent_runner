import numpy as np
import fiona
import rasterio
import rasterio.features
from affine import Affine
from shapely.geometry import shape



def rasterize(shp_name, raster_name, buffer_size, result_name):

    with fiona.open(shp_name, 'r') as vector, \
            rasterio.open(raster_name, 'r') as raster:

        # get the affine transform for the input data
        transform = raster.transform
        profile = raster.profile
        
        data = np.zeros(raster.shape)


        for feature in vector:
            # create a shapely geometry
            geometry = shape(feature['geometry']).buffer(buffer_size)

            # get pixel coordinates of the geometry's bounding box
            ul = raster.index(*geometry.bounds[0:2])
            lr = raster.index(*geometry.bounds[2:4])

            # read the subset of the data into a numpy array
            data[lr[0]: ul[0]+1, ul[1]: lr[1]+1] = 1


    with rasterio.open(result_name, 'w', **profile) as result:
        result.write(data.astype(rasterio.uint8), 1)



if __name__ == "__main__":
    buffer_dist = 0.05
    shp = 'samples\\parks.shp'
    raster_name = 'conf17938prim.tif'
    result_name = 'result.tif'

    rasterize(shp, raster_name, buffer_dist, result_name)

