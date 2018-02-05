ModelDataGrab.py is used to read data (MSLP data by default) from a GRIB file (tested with GFS data so far), read track data from a csv file (IrmaTrack.csv provided as an example of the format tested), and calculate error for a chosen time.

ModelErrorTally.py is used for error statistic calculations across multiple model data files for a single storm.

ErrorPlot.py generates a plot for the average error statistics by timeframe (24, 48, 72, 96, 120 hours).
