from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import matplotlib.pyplot as plt
import datetime as dt
import time

ts = TimeSeries(key='4NIIGXQ179RD4W12', output_format='pandas')
ti = TechIndicators(key='4NIIGXQ179RD4W12', output_format='pandas')

ticker = 'IBM'







macd, macd_data = ti.get_macd(ticker, '1min')
stock, stock_data = ts.get_intraday(ticker,'1min','full')


starttime=time.time()
timeDiff = time.time() - starttime
#currEpoch = (time.time()-60)//60*60
#currTime = dt.datetime.fromtimestamp(currEpoch)



currTime = dt.datetime(2020,6,8,9,40,0) #remove during real time



'''
open = float(stock.at[currTime, '1. open'][0])

high = float(stock.at[currTime, '2. high'][0])
low = float(stock.at[currTime, '3. low'][0])
vol = float(stock.at[currTime, '5. volume'][0])
'''


close = float(stock.at[str(currTime), '4. close'][0]) #remove

capital = 10000
noPos = True
takeProfit = close + 1
stopLoss = 0
vwapTotal = 0
vwapVol = 0
macdValue = 0
signalValue = 0




while timeDiff < 10800 or not noPos:

    macd, macd_data = ti.get_macd(ticker, '1min')
    stock, stock_data = ts.get_intraday(ticker,'1min','full')

    try:
        prevClose = close
    except:
        prevClose = float(stock.at[str(currTime), '4. close'][0])

    prevClose = close
    prevMacd = macdValue
    prevSignal = signalValue

    if len(macd.at[str(currTime), 'MACD']) == 1:
        macdValue = float(macd.at[str(currTime), 'MACD'][0])

    if len(macd.at[str(currTime), 'MACD_Signal']) == 1:
        signalValue = float(macd.at[str(currTime), 'MACD_Signal'][0])


    try:
        close = float(stock.at[str(currTime), '4. close'])
        high = float(stock.at[currTime, '2. high'])
        low = float(stock.at[currTime, '3. low'])
        vol = float(stock.at[currTime, '5. volume'])
        avgPrice = (high + low + close)/3
        vwapTotal += avgPrice * vol
        vwapVol += vol
        vwapValue = vwapTotal / vwapVol

    except:
        pass


    change = (close - prevClose)/prevClose

    #check if macd crossed signal
    if prevMacd < prevSignal and macdValue >= signalValue:
        macdCrossed = True
    else:
        macdCrossed = False

    #check if buy condition met
    if macdCrossed and close > vwapValue and noPos:

        posValue = capital - (capital % close)
        capital -= posValue
        noOfShares = posValue//close
        noPos = False
        stopLoss = close * 0.995
        takeProfit = close * 1.01
        print(str(currTime),'Bought', noOfShares,'shares of',ticker,'at',posValue)
    #check if sell condition met
    elif close < stopLoss or close > takeProfit:
        if not noPos:
            posValue *= (1 + change)
            capital += posValue
            stopLoss = 0
            takeProfit = close + 1
            noPos = True
            print(str(currTime),'Sold', noOfShares,'shares of',ticker,'at', posValue)

    else:
        print(str(currTime),ticker, (str(round((change*100),4))+'%'))


    currTime = dt.datetime.fromtimestamp(currTime.timestamp()+60)
    #timeDiff += 60
    time.sleep(60.0 - (timeDiff % 60.0))
    timeDiff = time.time() - starttime


print(capital)
