import sys
import csv
import numpy
import scipy
import pygrib
import metpy.calc
from geopy.distance import vincenty

resolution = 0
lat_min = 0
lat_max = 0
lon_min = 0
lon_max = 0

'''NOTE: Can probably iterate over a 2D array storing data rather than storing lat
lon, instead having a formula to convert when needed'''

def grab_file(file_path):
    '''Grabs a GRIB file at file_path and loads it in as a pygrib.open object'''
    return pygrib.open(file_path)

def grab_field(opened_grib, res, field = 'MSLP (Eta model reduction)'):
    '''Grabs the first grib message where name == field in opened_grib, defaulting
    to MSLP for most testing, as well as setting the global resolution'''
    global resolution
    resolution = float(res)
    return opened_grib.select(name = field)[0]

def load_data(grib_message, lat_lower = 5, lat_upper = 70, lon_lower = 250, lon_upper = 350):
    '''Gets data from geographical subset defined by lats and lons,
    setting latitude and longitude global bounds,
    returning a triple of the parameter, lats, and lons
    default bounds reflect vast majority of Atlantic data points'''
    global lat_min, lat_max, lon_min, lon_max
    lat_min = lat_lower
    lat_max = lat_upper
    lon_min = lon_lower
    lon_max = lon_upper
    return grib_message.values

def lat_to_index(lat):
    '''takes latitude data and transforms it into appropriate index'''
    return (lat_max-lat)/resolution

def index_to_lat(index):
    '''takes index and transforms it into appropriate latitude'''
    return lat_max-resolution*index

def lon_to_index(lon):
    '''takes longitude data and transforms it into appropriate index'''
    return (lon-lon_min)/resolution

def index_to_lon(index):
    '''takes index and transforms it into appropriate longitude'''
    return index*resolution+lon_min

def coordinates_to_indices(lat, lon):
    '''takes coordinate data and transforms it into appropriate indices for
    accessing the data array'''
    return lat_to_index(lat), lon_to_index(lon)

def indices_to_coordinates(row, col):
    '''takes indices and transforms them into corresponding coordinate data'''
    return index_to_lat(row), index_to_lon(col)

def grab_point(lat, lon, data):
    '''retrieves matching data point from a 2D array'''
    x, y = degrees_to_indices(lat, lon)
    return data[x][y]

def merge_data(data, lats, lons):
    '''Merges data, lats, lons (numpy ndarrays) into one 2D array with elements of
    the form [latitude, longitude, datum]'''
    return numpy.stack((lats, lons, data), axis = 2)

def locate_center(data, lat, lon):
    '''Locates tropical cyclone center based on a 4 degree search radius
    around best track center passed through lat, lon,
    returning triple of minimum, latitude, longitude'''
    '''Future implementation: parameters beyond MSLP to curb erroneous points,
    a means of determining whether to expand search radius based on reasonable
    values for these parameters'''

    #calculate starting and ending height of search box
    if lat - 4 < lat_min:
        h_start = lat_to_index(lat_min)
    else:
        h_start = lat_to_index(lat-4)
    if (lat + 4 > lat_max):
        h_end = lat_to_index(lat_max)
    else:
        h_end = lat_to_index(lat+4)

    #calculate starting and ending width of search box
    if lon - 4 < lon_min:
        w_start = lon_to_index(lon_min)
    else:
        w_start = lon_to_index(lon-4)
    if (lon + 4 > lon_max):
        w_end= lon_to_index(lon_max)
    else:
        w_end = lon_to_index(lon+4)


    #find minimum value in search radius
    minimum = float('inf')
    minimum_h = 0
    minimum_w = 0
    for h in range (int(h_end), int(h_start)+1):
        for w in range (int(w_start), int(w_end+1)):
            if data[h][w] < minimum:
                minimum = data[h][w]
                minimum_h = h
                minimum_w = w

    return minimum, index_to_lat(minimum_h), index_to_lon(minimum_w)

def calculate_position_error(model_lat, model_lon, real_lat, real_lon):
    '''calculates the distance between the model point and real point'''
    model = (model_lat, model_lon)
    real = (real_lat, real_lon)
    return vincenty(model,real).nm

def read_time(time, csvfile):
    '''returns the latitude and longitude for the matching time in the
    opened csvfile'''
    reader = csv.reader(csvfile, delimiter = ' ')
    csv_list = list(reader)

    lat = 0
    lon = 0
    time_index = -1
    lat_index = -1
    lon_index = -1
    index = 0
    while index < len(csv_list[0]):
        if csv_list[0][index] == 'TIME':
            time_index = index
        if csv_list[0][index] == 'LAT':
            lat_index = index
        if csv_list[0][index] == 'LON':
            lon_index = index
        index+=1
    if time_index == len(csv_list[0]):
            warnings.warn('No Time field found, abort')

    for line in csv_list:
        if line[time_index] == time:
            lat = line[lat_index]
            lon = line[lon_index]
            return float(lat), float(lon)

def main(model_file, track_file, time, res):
    '''takes an input GRIB2 model file (currently GFS files), a track file
    (currently an individual csv track file), a time of form 'MM/DD/HHZ',
    and the degree resolution of the model data, and computes the model error
    for the storm's position at that time'''
    track = open(track_file, 'r')
    lat, lon = read_time(time, track)
    mslp = grab_field(grab_file(model_file), res)
    mslp_data = load_data(mslp, lat-10, lat+10, lon-10, lon+10)
    _, model_lat, model_lon = locate_center(mslp_data, lat, lon)
    print(calculate_position_error(model_lat, model_lon, lat, lon))
    return calculate_position_error(model_lat, model_lon, lat, lon)

if __name__ == '__main__':
    model_file = sys.argv[1]
    track_file = sys.argv[2]
    time = sys.argv[3]
    res = sys.argv[4]
    main(model_file, track_file, time, res)
