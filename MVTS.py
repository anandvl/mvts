import pandas
import datetime
import io
import base64

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State

# User Input
defaultStartDate = datetime.date(2025, 11, 1)
defaultEndDate = datetime.date(2026, 12, 31)
inpDTformat = '%m-%d-%Y %I:%M %p'
pltDTformat = "%Y-%m-%d %H:%M:%S.%f"
cgmHist = pandas.DataFrame()

# Set up an interactive dash app
# From 'dataVis_XYZ.py' for batched data
dashApp = Dash(__name__)

# Set the layout of the app (primarily a 'datepicker')
# {'visibility': 'hidden/visible'} OR {'display' : 'none'/'block'}
dashApp.layout = html.Div([
    html.H3("Select CSV File to Upload ..."),
    dcc.Upload(id='uploadFile',
               children=html.Div([
                   'Drag and Drop or ',
                   html.A('Select Files')
               ]),
               style={
                   'width': '100%',
                   'height': '60px',
                   'lineHeight': '60px',
                   'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'borderRadius': '5px',
                   'textAlign': 'center',
                   'margin': '10px'
               },
               # Allow multiple files to be uploaded
               # multiple=True
               ),
    html.H4(id='dateRangeOutput'),
    html.H3(id='dateSelectTitle', children="Select the date of the analysis", style={'font-family': 'verdana', 'visibility': 'hidden'}),
    dcc.DatePickerSingle(
        id='date_Of_Interest',
        min_date_allowed=defaultStartDate,
        max_date_allowed=defaultEndDate,
        initial_visible_month=datetime.date.today(),
        date=datetime.date.today(),
        style={'font-family': 'verdana', 'width':'100%', 'height':'10px', 'display':'inline-block', 'visibility': 'hidden'}
    ),
    html.Div(id='showPlot', children=[
        dcc.Graph(id="time_series_plot")
    ], style={'visibility': 'hidden'})

],
    style={'height': 100,
           'margin-top': '0px',
           'margin-left': '10px',
           'font-size': '18px'}
)

# Load the user selected CSV file and output the range of data
@dashApp.callback(
    Output("dateRangeOutput", 'children'),
    Output('dateSelectTitle', 'style'),
    Output('date_Of_Interest', 'style'),
    Output('date_Of_Interest', 'min_date_allowed'),
    Output('date_Of_Interest', 'max_date_allowed'),
    Input('uploadFile', 'contents'),
    State('uploadFile', 'filename')
)
def loadData(contents, filename):
    global cgmHist

    if contents is not None:
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if ('csv' in filename) | ('CSV' in filename):
                cgmData = pandas.read_csv(io.StringIO(decoded.decode('utf-8')), header = 0, skiprows=1)

                # Clean up column names
                cgmData.columns = [x.strip().replace('-', '').replace(' ', '_') for x in list(cgmData.columns)]

                # Break apart the historical and scan data
                cgmHist = cgmData.loc[
                    cgmData.Record_Type == 0, ['Device_Timestamp', 'Historic_Glucose_mg/dL']].copy().rename(
                    columns={'Device_Timestamp': 'dateTime', 'Historic_Glucose_mg/dL': 'Glucose'}).reset_index(
                    drop=True)
                # cgmScan = cgmData.loc[cgmData.Record_Type==1,['Device_Timestamp', 'Scan_Glucose_mg/dL']].copy().rename(columns={'Device_Timestamp':'dateTime', 'Scan_Glucose_mg/dL': 'Glucose'}).reset_index(drop=True)

                # Convert dateTime to datetime format
                cgmHist.dateTime = pandas.to_datetime(cgmHist.dateTime, format=inpDTformat)
                # cgmScan.dateTime = pandas.to_datetime(cgmScan.dateTime, format=inpDTformat)

                # find the limits of data
                startDate = min(cgmHist.dateTime).date()
                endDate = max(cgmHist.dateTime).date()

            return (f'Read {filename} with {cgmData.shape[0]} rows of data ranging  {startDate.strftime("%m/%d/%y")} - {endDate.strftime("%m/%d/%y")}', {'visibility': 'visible'}, {'visibility': 'visible'}, startDate, endDate)
        except Exception as e:
            print(e)
            return ('There was an error processing this file.', {'visibility': 'hidden'}, {'visibility': 'hidden'}, defaultStartDate, defaultEndDate)
    else:
        return ('', {'visibility': 'hidden'}, {'visibility': 'hidden'}, defaultStartDate, defaultEndDate)

# Plot both the historical and scan data on the same graph
@dashApp.callback(
    Output("time_series_plot", "figure"),
    Output("showPlot", "style"),
    Input("date_Of_Interest", "date")
     )
def update_time_series_chart(date_value):
    global cgmHist
    # cgmHist = cgmHist_full.copy()
    if (cgmHist.shape[0] > 0):

        if date_value is not None:
            date_object = datetime.date.fromisoformat(date_value)
            startTime = date_object.strftime(pltDTformat).replace('T', ' ')
            # print(date_value, date_object, startTime)
        else:
            startTime = '2025-11-08 00:00:00'
        # Truncate to start and end times

        startTime = pandas.Timestamp(pandas.to_datetime(startTime, format=pltDTformat))
        # endTime = pandas.Timestamp(pandas.to_datetime(endTime, format=pltDTformat))

        endTime = pandas.Timestamp(pandas.to_datetime(startTime, format=pltDTformat)+datetime.timedelta(hours=24))

        # print(startTime)

        cgmHistSub = cgmHist.loc[(cgmHist.dateTime > startTime) & (cgmHist.dateTime < endTime),].copy().reset_index(drop=True)
        # cgmScanSub = cgmScan.loc[(cgmScan.dateTime > startTime) & (cgmScan.dateTime < endTime),].copy().reset_index(drop=True)
        # print(cgmHistSub.shape)


        fig = make_subplots(rows=1, cols=1)
        # fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02,
        #                     specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
        valueLT = 'Glucose'
        # valueRT = 'Cal_per_5min'
        # valueLB = 'dGlucose'
        # valueRB = 'HeartRate'

        unitLT = 'mg/dL'
        # unitRT = 'cals/5min'
        # unitLB = 'mg/dL/min'
        # unitRB = 'bpm'

        rangeLT = [70, 210]
        # rangeRT = [0, 300]
        # rangeLB = [-4, 4]
        # rangeRB = [40, 180]

        fig.add_trace(go.Scatter(x=cgmHistSub.dateTime, y=cgmHistSub[valueLT], mode='lines', name=f'{valueLT}', line=dict(color="#0000ff")), row=1, col=1)
        # fig.add_trace(go.Scatter(x=cgmScanSub.dateTime, y=cgmScanSub[valueLT], mode='lines', name=f'Scan_{valueLT}', line=dict(color="#ff0000")), row=1, col=1)

        fig.update_xaxes(title_text='Date and Time', row=1, col=1,
                         title_font=dict(color='black', size=18), tickcolor='black',
                         tickfont=dict(color='black', size=18))
        fig.update_yaxes(title_text = f'{valueLT} ({unitLT})', row=1, col=1, secondary_y=False,
                         title_font=dict(color='blue', size=18), tickcolor='blue',
                         range = rangeLT,
                         tickfont=dict(color='blue', size=18))

        '''
        fig.add_trace(go.Scatter(x=calDataSub.dateTime, y=calDataSub[valueRT],
                                 text=calDataSub.Description,
                                 hovertemplate = '%{x} %{y} <br>' + '%{text}<extra></extra>',
                                 mode='lines', name=f'{valueRT}', line=dict(color="#ff0000")),
                       secondary_y=True, row=1, col=1)
        fig.update_yaxes(title_text = f'{valueRT} ({unitRT})', row=1, col=1, secondary_y=True,
                         title_font=dict(color='red', size=18), tickcolor='red',
                         range = rangeRT,
                         tickfont=dict(color='red', size=18))

        fig.add_trace(go.Scatter(x=cgmHistSub.dateTime, y=cgmHistSub[valueLB], mode='lines', name=f'{valueLB}', line=dict(color="#0000ff")), row=2, col=1)
        fig.add_trace(go.Scatter(x=hrDataSub.dateTime, y=hrDataSub[valueRB], mode='lines', name=f'{valueRB}', line=dict(color="#ff0000")),
                      secondary_y=True, row=2, col=1)

        fig.update_yaxes(title_text = f'{valueLB} ({unitLB})', row=2, col=1, secondary_y=False,
                         title_font=dict(color='blue', size=18), tickcolor='blue',
                         range = rangeLB,
                         tickfont=dict(color='blue', size=18))
        fig.update_yaxes(title_text = f'{valueRB} ({unitRB})', row=2, col=1, secondary_y=True,
                         title_font=dict(color='red', size=18), tickcolor='red',
                         range = rangeRB,
                         tickfont=dict(color='red', size=18))

        '''
        # fig.update_layout(title=f'Time series of data', height=800)
        fig.update_layout(height=700)
        # return go.Figure(data=figData, layout=figLayout)
        return (fig, {'visibility': 'visible'})
    else:
        return ((go.Figure(go.Scatter(
            x=pandas.Series(dtype=object),
            y=pandas.Series(dtype=object),
            mode="markers")), {'visibility': 'hidden'})
        )


# Set debug=False so that the app does not get automatically reloaded each time an edit is made
dashApp.run_server(host="0.0.0.0", port=9000, debug=False, dev_tools_props_check=False)