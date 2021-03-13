import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import dash_daq as daq
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_table
import urllib
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

import base64
import datetime
import io
import time

app = dash.Dash(__name__)
app.title='DASH APP'

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.Div([

        html.Div([
            
            html.Div(
                style={'display': 'inline-block',
                'marginTop': '25px',
                'width': '80%',
                'fontWeight': 'bold',
                'fontSize': '44px',
                'user-select': 'none',
                'color': '#db0404'},
                children=['DASH APP',
                dbc.Badge('v.1.0', color="",
                style={
                    'vertical-align': 'top',
                    'margin': '0px',
                    'font-size': '14px',
                })]
            
            ),      
        ],style={'textAlign': 'center'}),

    ],style={
        'border': '5px black solid',
        'backgroundColor': '#639af2',
        'padding': '5px 5px'
    }),

    html.Div([
        html.Div([
            dcc.Upload(
                html.Button('Load Data', style={ 'color': '#ff8503', 'backgroundColor': '#625576', 'width': '80%', 'minWidth': '120px'}),
                id='load-data',
                multiple=True,
                style={'margin': '10px 0px', 'padding':'10px 0px','color': '#ff8503'}),

            html.Div(
                [dcc.Dropdown(
                id='field-dropdown',
                placeholder='Search for Signals',
                multi=True,
                style={ 'height': '120px', 'border': 'none', 'borderRadius': '10px',
                'margin': 'auto', 'color': '#ff8503', 'backgroundColor': '#625576',}
                )], style={'width': '95%', 'margin': 'auto', 
                'height': '230px','backgroundColor': '#625576',
                'border': 'solid white 1px', 'borderRadius': '10px','maxHeight': '230px','overflowY': 'scroll',}
            ),
            html.Div([
                html.Button(
                    'Run',
                    id='btn-run',
                    style={'height': '40px', 'margin': '5px 0px', 'color': '#ff8503', 'backgroundColor': '#625576', 'width': '80%', 'minWidth': '120px'}
                ),
                html.A(
                    html.Button(children='Export',
                    style={'height': '40px', 'margin': '5px 0px', 'color': '#ff8503', 'backgroundColor': '#625576', 'width': '80%', 'minWidth': '120px'}),
                    id='download-link',
                    download="ExportedData.csv",
                    href="",
                    target="_blank",
                    style={'height': '40px'}
                ),
                
            ], style={'padding': '15px 0px '}),
            

        ], style={'width': '15%', 'display': 'inline-block',
                  'textAlign': 'center', 
                  'border': '5px black solid','margin': '5px 0px'}),
        html.Div([

            html.Div([
                html.H4(
                    children='Output Sample Statistics Panel',
                    id='message',
                    style={'fontSize': '20px', 'textAlign': 'center', 
                    'fontWeight': '600', 'color': 'black', 'display': 'inline-block',
                    },
                ),
                ]
                , style={'borderBottom': '5px black solid',
                        'margin': '5px 5px',
                        },
            ),

            dcc.Loading(
                id="loading-1",
                type="cube",
                children=dcc.Graph(
                    #figure=fig,
                    id='graph-display',
                    style={'display': 'none'},
                ),
                style={'textAlign' : 'center','top': '50%'},
            ),

            html.Div(
                id='output-data-upload',
                style={'display': 'inline-block',
                'overflowY': 'scroll', 'maxHeight': 610,'overflowX': 'scroll', 'maxWidth': 1050}
            ),

        ], style={'width': '80%',
                  'display': 'inline-block',
                  'textAlign': 'center',
                  'float': 'right', 'margin': 'auto', 'marginRight': '20px'}),
    ],style={})
], style={
        'border': '5px black solid',
        'backgroundColor': '#639af2',
        'padding': '5px 5px' }
)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
        
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.',
            
        ], style={ 'color': 'black'})

    global dff
    dff=df

    return html.Div([
        html.H6([f'Your uploaded file: {filename}'], style={ 'color': 'black'}),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
        ),
])


@app.callback(Output('output-data-upload', 'children'),
              Input('load-data', 'contents'),
              State('load-data', 'filename'),
              State('load-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



@app.callback(
    Output('download-link', 'href'),
    [Input('output-data-upload', 'children')])
def update_download_link(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        
        
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        return csv_string


@app.callback(
    Output('field-dropdown', 'options'),
    [Input('output-data-upload', 'children')])
def update_my_output1(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return [{'label': i, 'value': i} for i in list(dff.columns.unique())]


@app.callback(
    Output('message', 'children'),
    [Input('output-data-upload', 'children')])
def update_my_output2(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return f'Your DataFrame has {len(dff)} rows and {len(dff.columns)} columns'


@app.callback(
    Output('graph-display', 'style'),
    Output('output-data-upload', 'style'),
    [Input('btn-run', 'n_clicks'),
    Input('output-data-upload', 'children')])
def update_my_output3(n_clicks1, n_clicks2):
    ctx = dash.callback_context
    flag = ctx.triggered[0]['prop_id'].split('.')[0]
    if n_clicks1 is None or n_clicks2 is None:
        raise PreventUpdate
    else:
        if flag == 'btn-run':
            time.sleep(3)
            return [{'display': 'inline-block'}, {'display': 'none'}]
        elif flag == 'output-data-upload':
            return [{'display': 'none'}, {'display': 'inline-block'}]


@app.callback(
    Output('graph-display', 'figure'),
    [Input('btn-run', 'n_clicks'),
    State('field-dropdown', 'value'),
    ])
def update_my_output_anogen(n_clicks1, val):
    if n_clicks1 is None:
        raise PreventUpdate
    else:

        fig = px.scatter(
            dff,
            x=val[0],
            y=val[1], 
            
            #trendline="lowess",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        fig.update_layout(
            
            width=800,
            height=450,
            )


        return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
