import numpy as np
import fiona
import rasterio
from shapely.geometry import shape


DTYPE = 'int32'  # np.dtype(int)

def rasterize(shp_name, raster_name, buffer_size, result_name):

    with fiona.open(shp_name, 'r') as vector, \
            rasterio.open(raster_name, 'r') as raster:

        # get the affine transform for the input data
        transform = raster.transform
        profile = raster.profile
        
        data = np.ones(raster.shape, dtype=DTYPE)


        for feature in vector:
            # create a shapely geometry
            geometry = shape(feature['geometry']).buffer(buffer_size)

            # get pixel coordinates of the geometry's bounding box
            ul = raster.index(*geometry.bounds[0:2])
            lr = raster.index(*geometry.bounds[2:4])

            # read the subset of the data into a numpy array
            data[int(lr[0]): int(ul[0]+1), int(ul[1]): int(lr[1]+1)] = 2


    with rasterio.Env():
        profile['dtype'] = DTYPE
        with rasterio.open(result_name, 'w', **profile) as result:
            result.write(data.astype(DTYPE), 1)



if __name__ == "__main__":
    import os

    buffer_dist = 0.05
    shp = os.path.join('samples','parks.shp')
    raster_name = os.path.join('samples','conf17938prim.tif')
    result_name = 'result.tif'

    rasterize(shp, raster_name, buffer_dist, result_name)

