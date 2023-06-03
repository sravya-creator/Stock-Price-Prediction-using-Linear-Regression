import dash
from dash import dash_table
from dash import dcc
from dash import html
from datetime import datetime as dt
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from pandas import *
from model import prediction
import numpy as np
import plotly as plt
import plotly.graph_objs as go
import plotly.express as px
import requests

def get_stock_price_graph(df):    #for plotting close and open vs Date
    fig = px.line(df,
                  x="Date",
                  y=["Adj Close"],hover_data={'Open':True,'value':False,'variable':False,'High':True,'Low':True,'Close':True},
                  title="Closing Price and Opening Price vs Date")
    newnames={"Adj Close":"Stock Price"}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    fig.update_layout(hovermode="y")
    
    return fig



app = dash.Dash(    
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Roboto&display=swap"
    ])
server = app.server 
app.layout = html.Div(
    [
        html.Div(
            [
                # Navigation
                html.P("Visualizing and Forecasting Stocks", className="start"),
                html.Div([
                    html.P("Enter stock code: "),
                    html.Div([
                        dcc.Input(id="dropdown_tickers", type="text"),
                        html.Button("Get Information", id='submit'),
                    ],
                             className="form")
                ],
                         className="input-place"),
                html.Div([
                    dcc.DatePickerRange(id='my-date-picker-range',
                                        min_date_allowed=dt(1995, 8, 5),
                                        max_date_allowed=dt.now(),
                                        initial_visible_month=dt.now(),
                                        end_date=dt.now().date()),
                ],
                         className="date"),
                html.Div([
                    html.Button(
                        "Stock Price Graph", className="stock-btn", id="stock"),
                    dcc.Input(id="n_days",
                              type="text",
                              placeholder="number of days"),
                    html.Button(
                        "Forecast", className="forecast-btn", id="forecast")
                ],
                         className="buttons"),
            ],
            className="nav"),

        # for the data plots
        html.Div(
            [
                html.Div(
                    [  # header
                        html.Img(id="logo"),
                        html.P(id="ticker")
                    ],
                    className="header"),
                html.Div(id="description", className="decription_ticker"),
                html.Div([html.P()],style={'padding':'5px'}),
                html.Div([html.P(id="Market Summary")],style={'font-weight':'bold','text-align':'center'}),
                html.Div([html.P()],style={'padding':'5px'}),
                html.Div([html.P(id="Opening Price Name"),html.P(id="Opening Price"),html.P(id="Currency Name"),html.P(id="currency")],style={'display': 'flex', 'justify-content': 'space-evenly'}),
                html.Div([html.P(id="High Price Name"),html.P(id="High Price"),html.P(id="52wkHigh Name"),html.P(id="52wkHigh")],style={'display': 'flex', 'justify-content': 'space-evenly'}),
                html.Div([html.P(id="Low Price Name"),html.P(id="Low Price"),html.P(id="52wkLow Name"),html.P(id="52wkLow")],style={'display': 'flex', 'justify-content': 'space-evenly'}),
                html.Div([html.P(id="Market Capital Name"),html.P(id="Market Capital"),html.P(id="Div yield Name"),html.P(id="Div yield")],style={'display': 'flex', 'justify-content': 'space-evenly'}),
                html.Div([], id="graphs-content"),
                html.Div([],id="table"),
                html.Div([], id="main-content"),
                html.Div([], id="forecast-content")
            ],
            className="content"),
    ],
    className="container")

# callback for company info
@app.callback([
    Output("description", "children"),
    Output("logo", "src"),
    Output("ticker", "children"),
    Output("Market Summary", "children"),
    Output("Opening Price Name","children"),
    Output("Opening Price", "children"),
    Output("Currency Name","children"),
    Output("currency", "children"),
    Output("High Price Name","children"),
    Output("High Price", "children"),
    Output("52wkHigh Name","children"),
    Output("52wkHigh", "children"),
    Output("Low Price Name","children"),
    Output("Low Price", "children"),
    Output("52wkLow Name","children"),
    Output("52wkLow", "children"),
    Output("Market Capital Name", "children"),
    Output("Market Capital", "children"),
    Output("Div yield Name", "children"),
    Output("Div yield", "children")
], [Input("submit", "n_clicks")], [State("dropdown_tickers", "value")])
def update_data(n, val): 
    if n == None:
        return "Please enter a legitimate stock code to get details.","", "","","","","","","","","","","","","","","","","",""
    else:
        if val == None:
            raise PreventUpdate
        else:
            api_key = "10cf41c5fc080b798083f9f27bd67ae1"
            ticker = yf.Ticker(val)
            x = ticker.fast_info
            # Use requests to get the company's summary data
            url = f"https://financialmodelingprep.com/api/v3/company/profile/{val}?apikey={api_key}"
            response = requests.get(url)
            data = response.json()
            url_change=f"https://financialmodelingprep.com/api/v3/stock-price-change/{val}?apikey={api_key}"
            response = requests.get(url_change)
            data_change = response.json()
            return data['profile']['description'],data['profile']['image'],data['profile']['companyName'],f'Market Summary',f'Open',round(x['open'],2),f'Currency',data['profile']['currency'],f'High',round(x['dayHigh'],2),f'52-wk high',round(x['yearHigh'],2),f'Low',round(x['dayLow'],2),f'52-wk low',round(x['yearLow'],2),f'%Change',round(data_change[0]['1D'],2),f'CurrentPrice',data['profile']['price']
# callback for stocks graphs
@app.callback([
    Output("graphs-content", "children"),
    Output("table","children")
], [
    Input("stock", "n_clicks"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
], [State("dropdown_tickers", "value")])

def stock_price(n, start_date, end_date, val):
    if n == None:
        return ["",""]
    if val == None:
        raise PreventUpdate
    else:
        '''x=read_csv('Yahoo-Finance-Ticker-Symbols.csv')
        names=x['Name'].to_list()
        tickers=x['Ticker'].to_list()
        if(val in names):
            ind=names.index(val)
            code=tickers[ind]
        else:
            code=val'''
        if start_date != None:
            df = yf.download(val, str(start_date), str(end_date))   #for downloading stock data b/w given dates
        else:
            df = yf.download(val)

    df.reset_index(inplace=True)
    #print(df)
    df['Open'] = np.round(df['Open'], 2)
    df['Close'] = np.round(df['Close'], 2)
    df['Low'] = np.round(df['Low'], 2)
    df['High'] = np.round(df['High'], 2)
    df['Adj Close'] = np.round(df['Adj Close'], 2)
    data = df.assign(Date=pd.to_datetime(df['Date']))
    df['Date'] = data['Date'].dt.date
    #df['Date'] = df['Date'].str.replace('T00:00:00', '')
    if(len(df.index)<=1):
        print("No value is displayed")
        fig = go.Figure()
        fig.update_layout(
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "No value is displayed,Please enter a correct date range",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 14
                    }
                }
            ]
        )

        return [dcc.Graph(figure=fig),""]
    else:
        table = go.Table(header=dict(values=list(df.columns)), cells=dict(values=[df[col] for col in df.columns]))
        tab=dash_table.DataTable(columns=[{"name": i, "id": i} for i in df.columns],data=df.to_dict('records'))
        fig = get_stock_price_graph(df)
        return [dcc.Graph(figure=fig),tab]


# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("dropdown_tickers", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days))
    return [dcc.Graph(figure=fig)]

if __name__ == '__main__':
    app.run_server(debug=True)