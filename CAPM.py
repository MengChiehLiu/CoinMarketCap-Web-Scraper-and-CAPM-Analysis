"""
coinmarketcap.com web scraper

Created on 2021-05-11 17:11:18

@author: Jack.M.Liu
"""

import pandas as pd
import matplotlib.pyplot as plt


def CAPM(df3,df4):
    df=df3
    #df = pd.read_csv (r'C:/Users/RiceBug/Desktop/df3.csv',index_col="Unnamed: 0")
    total_stock_list = df.columns
    coins = df.pct_change()
    coins = coins[1:]
    coins_sd = coins.std().tolist()
    #print(coins_sd)

    df1=df4
    #df1 = pd.read_csv (r'C:/Users/RiceBug/Desktop/df4.csv',index_col="Unnamed: 0")
    df1["markep cap"] = df1. sum(axis=1)
    market_cap_change = df1["markep cap"].pct_change()
    market_cap_change = market_cap_change[1:]
    market_SD = market_cap_change.std()
    #market_return = (1+market_cap_change.mean())**365-1  #天數
    market_return = market_cap_change.mean()*365
    coins = pd.concat([coins, market_cap_change], axis=1)

    covariance_matrix = coins.cov()
    #print(covariance_matrix)
    covariance_list = covariance_matrix.iloc[-1].tolist()
    covariance_list = covariance_list[:-1]
    #print(covariance_list)
    beta_list=[]
    for i in covariance_list:
        beta_list.append(i/market_SD**2)
    #print(beta_list)

    #CAPM
    risk_free = 0.09
    expected_return_list = []
    for i in beta_list:
        expected_return_list.append(risk_free + i*(market_return-risk_free))
    #print(expected_return_list)

    expected_return_df = pd.DataFrame()
    expected_return_df["beta"] = beta_list
    expected_return_df["expected return"] = expected_return_list
    expected_return_df['volatility'] = coins_sd
    expected_return_df.index = total_stock_list
    return expected_return_df

def main():
    df3 = pd.read_csv (r'C:/Users/RiceBug/Desktop/df3.csv',index_col="Unnamed: 0")
    df4 = pd.read_csv (r'C:/Users/RiceBug/Desktop/df4.csv',index_col="Unnamed: 0")
    df5 = CAPM(df3,df4)
    df5.to_csv('C:/Users/RiceBug/Desktop/df5.csv')

if __name__ == '__main__':
    main()
