def prediction(stock, n_days):
    import dash
    from dash import dcc
    from dash import html
    from datetime import datetime as dt
    import yfinance as yf
    from dash.dependencies import Input, Output, State
    from dash.exceptions import PreventUpdate
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error
    import plotly.graph_objs as go
    import plotly.express as px
    # model
    import numpy as np
    from datetime import date, timedelta
    data=yf.download(stock,period='5y')
    data.to_csv("stock_data.csv")
    StockData=pd.read_csv("stock_data.csv")

    # separate input (X) and output (y) variables
    X = StockData[['Open','High','Low']]
    y = StockData['Close']

    # split the data into training and testing sets
    split = int(0.8 * len(X))
    X_train = X[:split]
    y_train = y[:split]
    X_test = X[split:]
    y_test = y[split:]

    # create and train linear regression model
    reg = LinearRegression()
    reg.fit(X_train, y_train)

    # predict stock prices for next n days
    n = n_days
    future_days = StockData[-n:][['Open','High','Low']]
    future_prices = reg.predict(future_days)

    # evaluate the model on the test set
    y_pred = reg.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    #print(X_test,y_pred)

    dates = []
    current = date.today()
    for i in range(n_days):
        current += timedelta(days=1)
        dates.append(current)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,  # np.array(ten_days).flatten(), 
            y=future_prices,
            mode='lines+markers',
            name='data'))
    fig.update_layout(
        title="Predicted Close Price of next " + str(n_days) + " days",
        xaxis_title="Date",
        yaxis_title="Closed Price",
        # legend_title="Legend Title",
    )

    return fig