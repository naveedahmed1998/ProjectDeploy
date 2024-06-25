from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import yfinance as yf
from datetime import datetime
import pandas as pd
import dash_auth
# Project is dependent on Internet and yfinance library (pip install yfinance, if not yet)
# Check yfinance docs, because it might be updated.
# In the app you can select stocks from the dropdown menu, also you can use the date picker and hit submit
# to reload the information from the web. A lot of things we've already implemented in the past.
VALID_USERNAME_PASSWORD_PAIRS = {
    'naveed': 'ahmed'
}
app = Dash(__name__)

server = app.server

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
# Getting the data concerning the tickers list
# we want to use in our app:
nsdq = pd.read_csv('https://raw.githubusercontent.com/naveedahmed1998/DataRepo/main/NASDAQcompanylist.csv')
nsdq.set_index('Symbol', inplace = True) #'inplace' allows  us not to reassign it,
                                        # I mean instad of typing: nsdq = nsdq.set_index('Symbol')
options = []
for tic in nsdq.index:
    #{'label': 'user sees','value':'script sees'}
    mydict = {}
    mydict['label'] = nsdq.loc[tic]['Name']+''+tic # Apple Co. AAPL
    mydict['value'] = tic
    options.append(mydict)
    ## OR: options.append({'label':'{} {}'.format(tic, nsdq.loc[tic]['Name']),'value':tic})


app.layout = html.Div([
            html.H1('Stock Ticker Dashboard'),
            html.Div([html.H3('Enter a stock symbol:', style = {'paddingRight':'30px'}), # the text above dropdown
            #Changing Input to be a dropdown
            #dcc.Input(id = 'my_stock_picker',
                      #value = 'TSLA',
                      #style = {'fontSize':24, 'width':75}
            dcc.Dropdown(id = 'my_ticker_symbol',
                         options = options,
                         value = ['TSLA'],
                         multi = True # !Allows us to choose more than just one option in a dropdown menu.
            )], style = {'display':'iline-block', 'verticalAlign':'top', 'width':'40%'}),#width to have more space to chose
            html.Div([html.H3('Select a start and end date:'),
                      dcc.DatePickerRange(id = 'my_date_picker',
                                          initial_visible_month=datetime.today(),  # Needed for MCOS
                                          min_date_allowed='2015-1-1',
                                          max_date_allowed=datetime.today(),
                                          start_date='2020-1-1', # default date
                                          end_date=datetime.today(), # default date
                                          with_portal=True  # Needed for MCOS
                                          )
                      ], style = {'display':'inline-block'}),
            html.Div([
                    html.Button(id = 'submit-button',
                                          n_clicks = 0,
                                          children = 'Submit',
                                          style = {'fontSize': 24, 'marginLeft': '30px'}
                                          )
                      ]),
                      dcc.Graph(id = 'my_graph',
                                figure = {'data':[
                                    {'x':[1,2], 'y':[3,1]}
                        ], 'layout': {'title':'Default Title'}})])

@app.callback(Output('my_graph', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [State('my_ticker_symbol', 'value'),
               State('my_date_picker','start_date'),
               State('my_date_picker','end_date')
            ])
            # Step5. We keep the 'value', 'start_date', 'end_date' registered in its state, but don't send it
            # to update graph until we click on the submit button.
def update_graph(n_clicks, stock_ticker, start_date, end_date): #don't forget the date parameters, in the correct order
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')
    # Step 4. DatePicker range is dealing with datetime objects, HOWEVER,
    # The Input is grabbing its string representation! --> it won't work with yf.download--->
    # We need to reform this str to be a datetime object
    #https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

    # Step 6. We need to edit our function to take in those stocks coming from dropdown menu -
    # to create traces for each ticker in the list.
    traces = []
    for tic in stock_ticker:
        data = yf.download(tic, start, end) # data is a df
        traces.append({'x': data.index,'y': data['Close'], 'name': tic})
    fig = {
        'data': traces, #[{'x': data.index, 'y': data['Close']}],
        'layout': {'title': stock_ticker}
    }
    return fig
# Now the input box is interacting with the title.

if __name__ == '__main__':
    app.run(debug = True)