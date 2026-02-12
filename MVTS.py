import pandas
import datetime
import io
import base64

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
# import dash_daq as daq

# User Input
defaultStartDate = datetime.date(2025, 1, 1)
defaultEndDate = datetime.date(2026, 12, 31)
inpDTformat = '%m-%d-%Y %I:%M %p'
pltDTformat = "%Y-%m-%d %H:%M:%S.%f"
# rawData =  pandas.read_csv('/home/anand/tmpDocs/edocs/Misc/Health_Data/FreeStyle_Libre3/AnandLakshmikumaran_glucose_2-7-2026.csv', header = 0, skiprows=1)
rawData = pandas.DataFrame()
allData = pandas.DataFrame()
skipRows = 0 # number of rows to skip

# Set up an interactive dash app
# From 'dataVis_XYZ.py' for batched data
dashApp = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set the layout of the app (primarily a 'datepicker')
# {'visibility': 'hidden/visible'} OR {'display' : 'none'/'block'}

dashApp.layout = html.Div([
    dcc.Store(id='filteredData'),
    html.Datalist(id="timeformats", children=[
        html.Option(value=inpDTformat),
        html.Option(value=pltDTformat),
    ]),
    dbc.Container([
        dbc.Row([  # User Inputs
            dbc.Col([  # CSV file(s) to load
                html.H5("Select CSV File to Upload and numbers of rows to skip before the column header"),
                dcc.Input (id = 'inpNoOfRowsSkip', type = 'number', value=1),
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
                    }
                    # Allow multiple files to be uploaded
                    # multiple=True
                )
            ], width=4),
            # dbc.Col([  # Display file contents to decide further user inputs
            #    html.Div(id='dataTable')
            # ], width=3),
            dbc.Col([  # No. of rows to skip, time column, time format, data column(s)
                html.H6(id='outNoRows'),
                dcc.Input(id='inpTimeFormat', type='string', value=inpDTformat, list='timeformats', style={'visibility': 'hidden'}, debounce=True),
                dcc.Dropdown (id = 'inpTimeCol', options=list(allData.columns), value='', style={'visibility': 'hidden'}),
                dcc.Dropdown (id = 'inpDataColLT', options=list(allData.columns), value='', style={'visibility': 'hidden'}),

            ], width=4),
            dbc.Col([  # Could select the date or average over all dates
                html.H6(id='outDateRange'),
                html.H6(id='dateSelectTitle', children="Select date to plot",
                        style={'font-family': 'verdana', 'visibility': 'hidden'}),
                dcc.DatePickerSingle(
                    id='dateOfInterest',
                    min_date_allowed=defaultStartDate,
                    max_date_allowed=defaultEndDate,
                    disabled_days=[],
                    initial_visible_month=datetime.date.today(),
                    date=datetime.date.today(),
                    style={'font-family': 'verdana', 'width': '100%', 'height': '10px', 'display': 'inline-block',
                           'visibility': 'hidden'}
                ),
            ], width=4)
        ]),
        dbc.Row([ # Time-Series plot
            html.Div(id='showPlot', children=[
                dcc.Graph(id="time_series_plot")
            ], style={'visibility': 'hidden'})
        ])
    ], fluid=True),
    #  Put all tooltips here
    dbc.Tooltip([html.P('Use the following:'),
        html.P('%Y - Year with century (four digits) - 2026'),
        html.P('%y - Year without century (two digits) - 26'),
        html.P('%m - Month as a zero-padded decimal number - 02'),
        html.P('%B - Full month name - February'),
        html.P('%b - Abbreviated month name - Feb'),
        html.P('%d - Day of the month as a zero-padded decimal - 11'),
        html.P('%H - Hour (24-hour clock) as a zero-padded decimal - 18'),
        html.P('%I - Hour (12-hour clock) as a zero-padded decimal - 06'),
        html.P('%M - Minute as a zero-padded decimal number - 45'),
        html.P('%S - Second as a zero-padded decimal number - 30'),
        html.P('%p - AM or PM designation (need with %I above) - PM')
    ], target='inpTimeFormat'),
    dbc.Tooltip('This column will represent time as per the above format', target='inpTimeCol'),
    dbc.Tooltip('This column will represent first (of up to 4) Data - plotted on top left', target='inpDataColLT'),
],
    style={'height': 100,
           'margin-top': '0px',
           'margin-left': '10px',
           'font-size': '18px'}
)

# Load the user selected CSV file and output a sample of the data
#
# Output('dataTable', 'data'),
# Output('dataTable', 'columns'),
# Output('dataTable', 'children'),
@dashApp.callback(
Output("outNoRows", 'children'),
    Output('inpTimeFormat', 'style'),
    Output('inpTimeCol', 'options'),
    Output('inpTimeCol', 'style'),
    Output('inpDataColLT', 'options'),
    Output('inpDataColLT', 'style'),
    Input('uploadFile', 'contents'),
    State('uploadFile', 'filename'),
    State('inpNoOfRowsSkip', 'value')
)
def loadData(contents, filename, noRowsToSkip):
    global rawData, allData

    # rawData.to_dict('records')
    # f'{allData.shape[0]} rows of data from {startDate.strftime("%m/%d/%y")} to {endDate.strftime("%m/%d/%y")}'
    # html.Div(children = [html.H6(''), table_component]),
    # html.Div(children = [html.H6(''), table_component]),
    # print(f'{filename}')

    table_component = dash_table.DataTable(data = {}, columns = [{"name": i, "id": i} for i in rawData.columns],
                                            page_size = 5,
                                            fixed_rows={'headers': True},
                                            style_table = {'height': '150px', 'overflowY': 'auto'}
                                           )
    if contents is not None:  # Not an empty file
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if ('csv' in filename) | ('CSV' in filename):
                rawData = pandas.read_csv(io.StringIO(decoded.decode('utf-8')), header = 0, skiprows=noRowsToSkip)
            # print(f'{rawData.shape[0]}')
            table_component = dash_table.DataTable(data = rawData.to_dict('records'),
                                         columns = [{"name": i, "id": i} for i in rawData.columns],
                                         page_size = 5,
                                         fixed_rows={'headers': True},
                                         style_table = {'height': '150px', 'overflowY': 'auto'}
                                                   )
            return (f'{rawData.shape[0]} rows of data imported',
                    {'visibility': 'visible'}, list(rawData.columns), {'visibility': 'visible'}, list(rawData.columns), {'visibility': 'visible'})
        except Exception as e:
            print(e)
            return ('', {'visibility': 'hidden'}, [], {'visibility': 'hidden'}, [], {'visibility': 'hidden'})
    else:
        return ('', {'visibility': 'hidden'}, [], {'visibility': 'hidden'}, [], {'visibility': 'hidden'})

# Use number of rows to skip to extract actual data for analysis
@dashApp.callback(
Output("outDateRange", 'children'),
    Output('filteredData', 'data'),
    Output('dateSelectTitle', 'style'),
    Output('dateOfInterest', 'style'),
    Output('dateOfInterest', 'min_date_allowed'),
    Output('dateOfInterest', 'max_date_allowed'),
    Output('dateOfInterest', 'disabled_days'),
    Output('dateOfInterest', 'initial_visible_month'),
    Input('inpTimeCol', 'value'),
    Input('inpDataColLT', 'value'),
    State('inpTimeFormat', 'value'),
)
def filterData(timeCol, DataColLT, timeFormat):
    global rawData, allData

    # timeCol = 'Device Timestamp'
    # DataColLT = 'Historic Glucose mg/dL'

    if (rawData.shape[0] > 0) & (timeCol != '') & (DataColLT != ''):
        allData = rawData.loc[~pandas.isna(rawData[DataColLT]), [timeCol, DataColLT]].copy().reset_index(drop=True)

        # Convert dateTime to datetime format
        allData['dateTime'] = pandas.to_datetime(allData[timeCol], format=timeFormat)

        startDate = min(allData.dateTime).date()
        endDate = max(allData.dateTime).date()

        interval = datetime.timedelta(days=1)
        num_days = int((endDate - startDate) / interval) + 1
        validDays = [startDate + i * interval for i in range(num_days)]
        disabled_days = [j for j in validDays if j not in list(allData.dateTime.apply(lambda x: x.date()))]
        # print(f'{len(disabled_days)} out of {len(validDays)} days have no data')

        return (f'Dates from {startDate.strftime("%m/%d/%y")} to {endDate.strftime("%m/%d/%y")}',
                allData.to_json(date_format='iso', orient='split'), {'visibility': 'visible'}, {'visibility': 'visible'}, startDate, endDate, disabled_days, endDate)
    else:
        return ('', {}, {'visibility': 'hidden'}, {'visibility': 'hidden'}, defaultStartDate, defaultEndDate, [], datetime.datetime.today())

# Plot both the historical and scan data on the same graph
@dashApp.callback(
    Output("time_series_plot", "figure"),
    Output("showPlot", "style"),
    Input('filteredData', 'data'),
    Input("dateOfInterest", "date"),
    State('inpDataColLT', 'value'),
     )
def update_time_series_chart(allDataJ, date_value, DataColLT):
    global allData
    # allData = allData_full.copy()

    # if len(allDataJ) > 0:
    #    allData  = pandas.read_json(allDataJ, orient='split')

    if (allData.shape[0] > 0):

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

        allDataSub = allData.loc[(allData.dateTime > startTime) & (allData.dateTime < endTime),].copy().reset_index(drop=True)
        # cgmScanSub = cgmScan.loc[(cgmScan.dateTime > startTime) & (cgmScan.dateTime < endTime),].copy().reset_index(drop=True)
        # print(allDataSub.shape)


        fig = make_subplots(rows=1, cols=1)
        # fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02,
        #                     specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
        valueLT = DataColLT
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

        fig.add_trace(go.Scatter(x=allDataSub.dateTime, y=allDataSub[valueLT], mode='lines', name=f'{valueLT}', line=dict(color="#0000ff")), row=1, col=1)
        # fig.add_trace(go.Scatter(x=cgmScanSub.dateTime, y=cgmScanSub[valueLT], mode='lines', name=f'Scan_{valueLT}', line=dict(color="#ff0000")), row=1, col=1)

        fig.update_xaxes(title_text='Date and Time', row=1, col=1,
                         title_font=dict(color='black', size=18), tickcolor='black',
                         tickfont=dict(color='black', size=18))
        # f'{valueLT} ({unitLT})'
        fig.update_yaxes(title_text = f'{valueLT}', row=1, col=1, secondary_y=False,
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

        fig.add_trace(go.Scatter(x=allDataSub.dateTime, y=allDataSub[valueLB], mode='lines', name=f'{valueLB}', line=dict(color="#0000ff")), row=2, col=1)
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