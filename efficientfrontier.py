"""
coinmarketcap.com web scraper

Created on 2021-05-08 23:45:18

@author: Jack.M.Liu
"""

import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import scipy.optimize as solver
from functools import reduce
from coinmarketcap import coinmarketcap
from CAPM import CAPM
'''
df_close_price, df_market_cap =coinmarketcap("01/01/2021","10/05/2021")
df_CAPM = CAPM(df_close_price, df_market_cap)
df_CAPM = df_CAPM.T
'''
#df=df_close_price
df = pd.read_csv (r'C:/Users/RiceBug/Desktop/df3.csv',index_col="Unnamed: 0")
df_CAPM = pd.read_csv (r'C:/Users/RiceBug/Desktop/df5.csv',index_col="Unnamed: 0")
df_CAPM = df_CAPM.T

stable_coins_list = ['tether', 'usd-coin','wrapped-bitcoin','binance-usd','dai','terrausd',
                    'trueusd','reserve-rights','paxos-standard','husd','neutrino-usd','vai']
for i in stable_coins_list:  #Remove stable coins
    try:
        del df[i]
        del df_CAPM[i]
    except:
        pass

df_CAPM = df_CAPM.T
df = df.iloc[:,:20]
df_CAPM = df_CAPM.iloc[:20,:]

total_stock = len(df.columns)
returns = df.pct_change()
returns = returns[1:]

covariance_matrix = returns.cov() * 365 ** 0.5
#print(covariance_matrix)

stocks_expected_return = df_CAPM["expected return"]
#stocks_expected_return = returns.mean() * 365 #df.mean(axis = 0) is used to calculate the mean value of each column
'''
stocks_expected_return = []
for i in daily_stocks_expected_return :
    stocks_expected_return.append((1+i)**150-1)
'''

percentage = 1/total_stock
stocks_weights = np.array([])
for i in range(total_stock):
    stocks_weights = np.append(stocks_weights, [percentage])
#print(stocks_weights)

'''
portfolio_return = sum(stocks_weights * stocks_expected_return)
portfolio_risk = np.sqrt(reduce(np.dot, [stocks_weights, covariance_matrix, stocks_weights.T]))
print('投資組合預期報酬率為: '+ str(round(portfolio_return,4)))
print('投資組合風險為: ' + str(round(portfolio_risk,4)))
'''
#reduce(function,[1st,2nd,3rd...]), which have the function go on the first two object, and use the result to go on next one 
#np.dot() returns the dot product of two arrays
#portfolio risk formula:
#https://financetrain.com/how-to-calculate-portfolio-risk-and-return/



#try

risk_list = []
return_list = []

count = 0
stop = 100000
while count < stop:
    try:
        count += 1
        weight = np.random.rand(total_stock)
        weight = weight / sum(weight)
        return_list.append(sum(stocks_expected_return * weight))
        risk_list.append(np.sqrt(reduce(np.dot, [weight, covariance_matrix, weight.T])))
    except:
        pass
    print('\r' + '[Plotting]:[%s%s]%.2f%%;' % ('█' * int(count*20/stop), ' ' * (20-int(count*20/stop)),float(count/stop*100)), end='')
print()

#draw picture

'''
fig = plt.figure(figsize = (10,6))
fig.suptitle('Stochastic simulation results', fontsize=18, fontweight='bold')
ax = fig.add_subplot()
ax.plot(risk_list, return_list, 'o')
ax.set_title('n=1,000,000', fontsize=16)
plt.show()
#fig.savefig('result.png',dpi=300)
'''

#find portfolio with minimum risk 

def standard_deviation(weights):
    return np.sqrt(reduce(np.dot, [weights, covariance_matrix, weights.T]))

x0 = stocks_weights
bounds = tuple((0, 1) for x in range(total_stock))
#((0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)...)
constraints = [{'type': 'eq', 'fun': lambda x: sum(x) - 1}]
minimize_variance = solver.minimize(standard_deviation, x0=x0, constraints=constraints, bounds=bounds)
mvp_risk = minimize_variance.fun # .fun : get the output of the function
mvp_return = sum(minimize_variance.x * stocks_expected_return) # .x : get the intput of the function

#print('風險最小化投資組合預期報酬率為:' + str(round(mvp_return,2)))
#print('風險最小化投資組合風險為:' + str(round(mvp_risk,2)))
#for i in range(total_stock):
#    print(str(df.columns[i])+' 佔投資組合權重 : ' + str(format(minimize_variance.x[i], '.4f')))


#efficient frontier 

x0 = stocks_weights
bounds = tuple((0, 1) for x in range(total_stock))

efficient_fronter_return_range = np.arange(2, 6, .05)
efficient_fronter_risk_list = []

for i in efficient_fronter_return_range:
    constraints = [{'type': 'eq', 'fun': lambda x: sum(x) - 1},
                   {'type': 'eq', 'fun': lambda x: sum(x * stocks_expected_return) - i}]
    efficient_fronter = solver.minimize(standard_deviation, x0=x0, constraints=constraints, bounds=bounds)
    efficient_fronter_risk_list.append(efficient_fronter.fun)
    print('\r' + '[Efficient Frontier]:[%s%s]%.2f%%;' % ('█' * int(count*20/stop), ' ' * (20-int(count*20/stop)),float(count/stop*100)), end='')
print()



#best portfolio(sharpe ratio)
def negative_s_ratio(weights):
    sd = standard_deviation(weights)
    rt = sum(weights * stocks_expected_return)
    return -(rt - risk_free) / sd

risk_free = 0.09
constraints = [{'type': 'eq', 'fun': lambda x: sum(x) - 1}]
solution = solver.minimize(negative_s_ratio, x0=x0, constraints=constraints, bounds=bounds)
sharpe = solution.fun * (-1)
proportions = solution.x
best_risk = standard_deviation(proportions)
best_return = sum(proportions * stocks_expected_return)
boxtext=''
str_return = 'Portfolio Return: ' + str(format(round(best_return,4)*100, '.2f'))+ " %\n"
str_risk = 'Portfolio Risk: ' +  str(format(round(best_risk,4)*100, '.2f'))+ " %\n"
str_sharpe = 'Sharpe: ' + str(round(sharpe,4))+"\n"
boxtext = str_return + str_risk + str_sharpe + "\nProportions:\n"
for i in range(total_stock):
    if round(proportions[i],2) != 0:
        if i != (total_stock-1):
            boxtext += (str(df.columns[i])+': ' + str(format(proportions[i]*100, '.2f'))+ " %\n")
        else:
            boxtext += (str(df.columns[i])+': ' + str(format(proportions[i]*100, '.2f')))
    else:
        pass


#draw picture

fig = plt.figure(figsize = (12,6))
fig.subplots_adjust(top=0.85)
ax = fig.add_subplot()

fig.subplots_adjust(top=0.85)
ax0 = ax.scatter(risk_list, return_list,
                c=(np.array(return_list)-risk_free)/np.array(risk_list),
                marker = 'o')
ax.plot(efficient_fronter_risk_list, efficient_fronter_return_range, linewidth=1, color='#251f6b', marker='o', markerfacecolor='#251f6b', markersize=5)
#ax.plot(mvp_risk, mvp_return,'*',color='g',  markersize=25)
ax.plot(best_risk, best_return,'*',color='r',   markersize=25)
ax.axline((0, risk_free), slope=sharpe, color='r', linewidth=1, label='Capital Market Line')
ax.legend()
plt.xlim(0.1, 0.4), plt.ylim(2, 5)
print(boxtext)
'''
ax.text(0.4, 1, boxtext, style='italic',
        bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 10})
'''


ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_title('Efficient Frontier', fontsize=22, fontweight='bold')
ax.set_xlabel('Risk')
ax.set_ylabel('Return')
fig.colorbar(ax0, ax=ax, label = 'Sharpe Ratio')
plt.show()
#plt.savefig('Efficient_Frontier.png',dpi=300)

