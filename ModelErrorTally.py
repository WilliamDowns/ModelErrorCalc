import sys
import csv
import re
import datetime
from os import listdir
from os.path import isfile, join
import numpy
import scipy
import pygrib
from ModelDataGrab import main as calc_error

def get_time_and_date(data_name):
    '''REGEX through string to find model run date of form YYYYMMDDHH and forecast
    hour of form fHHH, returning correctly formatted day/month/hour and the
    lead time'''
    full_date_string = re.findall('[0-9]{10}', data_name)[0]
    time_string = re.findall('f[0-9]{3}', data_name)[0]
    target_time = datetime.datetime.strptime(full_date_string, '%Y%m%d%H') + datetime.timedelta(hours = int(time_string[1:]))
    return time_string[1:], target_time.strftime('%m/%d/%HZ')

def time_error(data_name, data_dir, csv_name, resolution):
    '''takes a CSV hurricane track file and a GRIB2 data file (currently GFS data)
    and calculates appropriate track error for that model in addition to returning
    its lead time'''

    time, date = get_time_and_date(data_name)
    error = calc_error(data_dir + '/' + data_name, csv_name, date, resolution)
    return time, error

def main(csv_name, model_dir, resolution):
    '''creates structures of model error data given a CSV hurricane track file and
    a directory containing GRIB2 forecast files of a constant horizontal resolution
    '''
    data_files = [data for data in listdir(model_dir) if isfile(join(model_dir, data))]
    #5 row array of lists for 24, 48, 72, 96, 120hr errors
    error_array = numpy.array([[1.1], [], [], [], []])
    #fun little navigation of numpy array to get a proper initialization of empty lists
    error_array[0].remove(1.1)
    hour_index = {'024': 0, '048': 1, '072': 2, '096': 3, '120': 4}
    for data in data_files:
        time, error = time_error(data, model_dir, csv_name, resolution)
        error_array[hour_index[time]].append(error)
    return error_array




if __name__ == '__main__':
    csv_name = sys.argv[1]
    model_dir = sys.argv[2]
    resolution = sys.argv[3]
    main(csv_name, model_dir, resolution)
