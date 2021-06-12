"""
coinmarketcap.com web scraper

Created on Sat May 8 02:43:06 2021

@author: Jack.M.Liu
"""

import numpy as np
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import time
import datetime
import json
import matplotlib.pyplot as plt


def date_to_timestamp(s,e):
    start = str(time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple()))[:-2]
    end = str(time.mktime(datetime.datetime.strptime(e, "%d/%m/%Y").timetuple())+86400)[:-2]
    return start ,end

def coinmarketcap(start_date,end_date):
    url = 'https://coinmarketcap.com/zh-tw/'
    response = rq.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    data= soup.find('script',id="__NEXT_DATA__",type="application/json")

    coins={}
    coin_data=json.loads(data.contents[0])
    listings=coin_data["props"]["initialState"]["cryptocurrency"]['listingLatest']['data']
    for i in listings:
        coins[str(i['id'])]=i['slug']

    start , end = date_to_timestamp(start_date,end_date) 

    percent=0
    total=100

    df2 = pd.DataFrame(columns=["Coin","Expected Return","Volatility"]) #volatility analysis
    df3 = pd.DataFrame() #Close Price
    df4 = pd.DataFrame() #Market Cap

    for coin in coins:
        Market_Cap=[]
        Open=[]
        High=[]
        Low=[]
        Volume=[]
        Close=[]
        Date=[]
        
        #print(coins[coin]+" historical data")
        try:
            url="https://web-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical?id="+coin+"&convert=USD&time_start="+start+"&time_end="+end
            response = rq.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            history_data = json.loads(soup.contents[0])
            quotes = history_data["data"]['quotes']
            for quote in quotes:
                time.sleep(0.01)
                Market_Cap.append(quote["quote"]["USD"]["market_cap"])
                Open.append(quote["quote"]["USD"]["open"])
                Date.append(quote["quote"]["USD"]["timestamp"][:10])
                High.append(quote["quote"]["USD"]["high"])
                Low.append(quote["quote"]["USD"]["low"])
                Volume.append(quote["quote"]["USD"]["volume"])
                Close.append(quote["quote"]["USD"]["close"])
            
            df = pd.DataFrame(columns=['Date','Open','High','Low','Close','Volume','Market Cap']) #All Coins' Data
            df['Date']=Date
            df['Open']=Open
            df['High']=High
            df['Low']=Low
            df['Close']=Close
            df['Volume']=Volume
            df['Market Cap']=Market_Cap
            
            df3['%s' %coins[coin] ] = df['Close']
            df4['%s' %coins[coin] ] = df['Market Cap']
            

            # volatility analysis
            '''
            df['Log Return']=np.log(df['Close']).diff(1)
            df['Cummulative Return']=np.exp(np.cumsum(df['Log Return']))-1
            Expected_Return = df['Cummulative Return'].tolist()[-1]
            Volatility = df['Log Return'].std()*(365**0.5)
            #print("Volatility of " + coins[coin] +" : " +str(Volatility))
            new_row = {"Coin":coins[coin],"Expected Return":Expected_Return,"Volatility":Volatility}
            df2 = df2.append(new_row, ignore_index=True)
            '''

            #draw pictire
            '''
            fig,ax = plt.subplots()
            df['Log Return'].hist(ax=ax ,bins=50, alpha=0.5,color="b")
            ax.set_xlabel("Log Return")
            ax.set_ylabel("Freq of Log Return")
            ax.set_title("Volatility of " + coins[coin] +" : " +str(round(Volatility,4)*100) +" %")
            plt.show()
            '''

            #plt.plot(df['Date'],df['Cummulative Return'])
            #plt.show()
            #df.to_csv('C:/Users/RiceBug/Desktop/coinmarketcap.com/'+coins[coin]+'.csv')
            #print(df)
            #print()

        except:
            pass
            
        percent+=1
        print('\r' + '[Web Scraping]:[%s%s]%.2f%%;' % ('█' * int(percent*20/total), ' ' * (20-int(percent*20/total)),float(percent/total*100)), end='')
        
    print()
    #print(df2)

    #df2.to_csv('C:/Users/RiceBug/Desktop/coinmarketcap.com.csv')

    df3.index = Date
    #df3.to_csv('C:/Users/RiceBug/Desktop/df3.csv')
    df4.index = Date
    #df4.to_csv('C:/Users/RiceBug/Desktop/df4.csv')
    return df3 , df4

def main():
    df3,df4 = coinmarketcap("01/12/2020","10/05/2021")
    df3.to_csv('C:/Users/RiceBug/Desktop/df3.csv')
    df4.to_csv('C:/Users/RiceBug/Desktop/df4.csv')

if __name__ == '__main__':
    main()


    


