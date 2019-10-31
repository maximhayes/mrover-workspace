%% GeoTiff Data Extractor

[landscape, SpatialReferencingObject] = geotiffread('GDAL_ADF_2_GeoTIFF.tif');
figure(1);
mapshow(landscape, SpatialReferencingObject);
