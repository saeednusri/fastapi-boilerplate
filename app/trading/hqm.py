import numpy as np
import pandas as pd
import math
import requests
from scipy.stats import percentileofscore as score
import xlsxwriter
from statistics import mean
from app.trading.secrets import IEX_CLOUD_API_TOKEN


def gethqm():
    portfolio_size=100000
    stocks=pd.read_csv("sp_500_stocks.csv")


    portfolio_input=100000

    # Function sourced from 
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]   
            
    symbol_groups = list(chunks(stocks['Ticker'], 100))
    symbol_strings = []
    for i in range(0, len(symbol_groups)):
        symbol_strings.append(','.join(symbol_groups[i]))
    #     print(symbol_strings[i])

    hqm_columns = [
                    'Ticker', 
                    'Price', 
                    'Number of Shares to Buy', 
                    'One-Year Price Return', 
                    'One-Year Return Percentile',
                    'Six-Month Price Return',
                    'Six-Month Return Percentile',
                    'Three-Month Price Return',
                    'Three-Month Return Percentile',
                    'One-Month Price Return',
                    'One-Month Return Percentile',
                    'HQM Score'
                    ]

    hqm_dataframe = pd.DataFrame(columns = hqm_columns)

    for symbol_string in symbol_strings:
    #     print(symbol_strings)
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            hqm_dataframe = hqm_dataframe.append(
                                            pd.Series([symbol, 
                                                    data[symbol]['quote']['latestPrice'],
                                                    'N/A',
                                                    data[symbol]['stats']['year1ChangePercent'],
                                                    'N/A',
                                                    data[symbol]['stats']['month6ChangePercent'],
                                                    'N/A',
                                                    data[symbol]['stats']['month3ChangePercent'],
                                                    'N/A',
                                                    data[symbol]['stats']['month1ChangePercent'],
                                                    'N/A',
                                                    'N/A'
                                                    ], 
                                                    index = hqm_columns), 
                                            ignore_index = True)

    filtered_df = hqm_dataframe[hqm_dataframe['One-Year Price Return'].isnull()]
    hqm_dataframe = hqm_dataframe.drop(filtered_df.index)
    
    time_periods = [
                    'One-Year',
                    'Six-Month',
                    'Three-Month',
                    'One-Month'
                    ]



    for row in hqm_dataframe.index:
        for time_period in time_periods:
            change_col = f'{time_period} Price Return'
            percentile_col = f'{time_period} Return Percentile'
            hqm_dataframe.loc[row, percentile_col] = score(hqm_dataframe[change_col], 
                                                        hqm_dataframe.loc[row, change_col], kind="strict")


    hqm_dataframe.sort_values(by = 'HQM Score', ascending = False, inplace=True)
    hqm_dataframe = hqm_dataframe[:51]
    hqm_dataframe.reset_index(inplace=True, drop=True)

    position_size = float(portfolio_size) / len(hqm_dataframe.index)
    for i in hqm_dataframe.index:
        hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe['Price'][i])

    hqm_dataframe.to_csv("hqm.csv")

    return 'Table Uploaded to BQ'



