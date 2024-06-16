"""
This script calculates the Normalized Difference Vegetation Index (NDVI) for a specified area of interest (AOI) 
and generates a DataFrame with mean NDVI values over time. The script uses Google Earth Engine (GEE) 
and pandas for data manipulation and analysis.

Functions:
    ndvi(image): Computes the NDVI for a given satellite image.
    aoi_ndvi_mean(image): Calculates the mean NDVI for the AOI and assigns a date to the result.
    create_ndvi_mean_dataframe(feature_collection): Creates a pandas DataFrame from the feature collection
    containing dates and mean NDVI values.

Usage:
    1. Define the area of interest (AOI) as a random point with a buffer.
    2. Map the `ndvi` and `aoi_ndvi_mean` functions over an ImageCollection to generate a feature collection.
    3. Convert the feature collection to a pandas DataFrame using `create_ndvi_mean_dataframe`.

Example:
    random_point = ee.Geometry.Point([-61.62448999387607, -10.486025731281506])
    aoi = random_point.buffer(30)

    image_collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
                        .filterBounds(aoi) \
                        .filterDate('2020-01-01', '2020-12-31') \
                        .map(ndvi) \
                        .map(aoi_ndvi_mean)

    feature_collection = image_collection.getInfo()
    df_ndvi_mean = create_ndvi_mean_dataframe(feature_collection)
    print(df_ndvi_mean)
"""

import ee
import pandas as pd

# Define a random point and buffer to create the area of interest (AOI)
random_point = ee.Geometry.Point([-61.62448999387607, -10.486025731281506])
aoi = random_point.buffer(30)

def ndvi(image):
    """
    Computes the NDVI for a given satellite image.

    NDVI is calculated as (NIR - Red) / (NIR + Red), where NIR and Red are the near-infrared 
    and red bands of the image, respectively.

    Args:
        image (ee.Image): The input satellite image.

    Returns:
        ee.Image: The input image with an additional NDVI band.
    """
    # Select the red and near-infrared bands
    red = image.select('B4')
    nir = image.select('B5')
    
    # Calculate NDVI
    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    
    # Add the NDVI band to the image
    return image.addBands(ndvi)

def aoi_ndvi_mean(image):
    """
    Calculates the mean NDVI for the AOI and assigns a date to the result.

    Args:
        image (ee.Image): The input satellite image with NDVI band.

    Returns:
        ee.Feature: A feature containing the date and mean NDVI value.
    """
    # Extract the date from the image metadata
    date = ee.Date(image.get('system:time_start')).format("YYYY-MM-dd", 'UTC')
    
    # Calculate the mean NDVI value within the AOI
    mean = image.select('NDVI').reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=aoi
    ).get('NDVI')
    
    # Return the date and mean NDVI as a feature
    return ee.Feature(None, {
        'date': date,
        'mean_ndvi': mean
    })

def create_ndvi_mean_dataframe(feature_collection):
    """
    Creates a pandas DataFrame from the feature collection containing dates and mean NDVI values.

    Args:
        feature_collection (dict): The input feature collection.

    Returns:
        pd.DataFrame: A DataFrame with sorted dates and corresponding mean NDVI values.
    """
    # Extract dates and mean NDVI values from the feature collection
    dates = [feature['properties']['date'] for feature in feature_collection['features']]
    mean_ndvi = [features['properties']['mean_ndvi'] for features in feature_collection['features']]
    
    # Create a DataFrame from the extracted data
    df = pd.DataFrame({
        'Date': dates,
        'Mean_NDVI': mean_ndvi
    })
    
    # Sort the DataFrame by date
    df_sorted = df.sort_values(by='Date')
    
    return df_sorted

