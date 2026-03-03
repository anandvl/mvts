# mvts
Multi-Variable Time Series Visualization and analysis, when time-series data is located in CSV file(s)

Implemented in Python using the plotly-dash framework.  

## To run:

#### On Linux, Windows, and Mac:

1. Install python

2. Install all packages in requirements.txt

		pip install -r requirements.txt

3. Run MVTS.py

		python MVTS.py

#### On Windows only:

Run the .exe file

#### For all:
The end result is a web server that will be started on port 9000.  Access it in any web-browser (tested only on Chrome and Safari) at 'http://localhost:9000'

## User Interface:
This app is currently designed to load and view CSV data from the FreeLibre 3 Continous Glucose monitoring (CGM) device.  An individual with a FreeLibre account can download CGM data in their account from [LibreView](https://www.libreview.com/). 

>TBD: Refine to address similar time-series data from other CSV files

>TBD: Refine to include plots of multiple time-series variables

***

- Drag and drop OR select a single CSV file to analyze.  But, make sure you have appropriately entered the number of lines to skip in the CSV file before you the column headers will show up. 

	*For a FreeLibre 3 CGM CSV file, the number of rows to skip is 1.*

>TBD: Have an option to view the CSV file and decide on the number of lines to skip
>
>TBD: Be able to analyze CSV file with no column headers (define column names based on the column number)

- Once the file is selected, more options will open up to identify the columns for the 'time' and 'data', and to type out the format of the time in the time column (review the tooltips for each of the entry. 

	*For a FreeLibre 3 CGM CSV file, the 'time'  and 'data' columns are 'Device Timestamp' and 'Historic Glucose mg/dL', respectively.  The time format is '%m-%d-%Y %I:%M %p', which will be input as default.*

- Once these are chosen, more options will open up for the user to select a date for which to plot the time-series data.  The minimum and maximum date  will be displayed and dates for which there are no data will be grayed out.  

- Once the user selects the date, an interactive plot will be displayed for that specific date.  Here are some ways to interact with the plot.  Note: At any instance, to get back to the default plot, hover the mouse near the top right section of the plot area (above the actual plot), and click on the the 'home' icon amongst the list of icons that shows up.

	Draw a rectangle anywhere on the plot with the left mouse button to zoom on the graph, both for the time and data.  To just zoom in one of the axis only, draw an horizontal or vertical line with the left mouse button. 

	To stretch the axis on one of the 4 corners, place the mouse at the appropriate corner, click the left mouse button and drag it to the right or left (or up and down).  Doing the same at the middle of the axis, will let you 'pan' along that axis.

	Hovering the mouse over the blue line will show a tooltip with the information (time and data value) for the corresponding point.

>TBD: Provide an option for the user to plot an averaged data with additional options to select the range of dates OR a list of dates over which the average will be calculated.  Options will also be provided to additionally plot an analysis of the range of data (at the specific instant) in addition to the average value.  
