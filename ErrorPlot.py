import sys
import numpy
import scipy
import ModelErrorTally
import matplotlib.pyplot as plot


def main(csv_name, model_dir, resolution):
    '''Generates a plot of model error data for the tropical cyclone in the
    csv file from all model data files in the model directory'''
    error_data = ModelErrorTally.main(csv_name, model_dir, resolution)
    averages = []
    i = 0;
    while i < error_data.size:
        averages.append(numpy.mean(error_data[i]))
        i+=1
    plot.plot([24, 48, 72, 96, 120], averages)
    plot.xticks(numpy.arange(24, 144, 24))
    plot.show()

if __name__ == '__main__':
    csv_name = sys.argv[1]
    model_dir = sys.argv[2]
    resolution = sys.argv[3]
    main(csv_name, model_dir, resolution)
