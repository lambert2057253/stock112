# Technical_Analysis.py
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data
import yfinance as yf
import datetime
import talib
import mpl_finance as mpf
import matplotlib.pyplot as plt
import Imgur

# 設定顏色
color = ['#2196f3', '#4caf50', '#ffc107', '#f436c7', '#f27521', '#e00b0b']

def TheConstructor(userstock):
    start = datetime.datetime.now() - datetime.timedelta(days=365)
    end = datetime.date.today()
    
    pd.core.common.is_list_like = pd.api.types.is_list_like
    yf.pdr_override()
    
    try:
        stock = data.get_data_yahoo(userstock + '.TW', start, end)
    except:
        stock = 'https://i.imgur.com/RFmkvQX.jpg'
    
    return stock

# MACD 圖
def MACD_pic(userstock, msg):
    stock = TheConstructor(userstock)
    ret = pd.DataFrame()
    
    if isinstance(stock, str):
        return stock
    
    ret['MACD'], ret['MACDsignal'], ret['MACDhist'] = talib.MACD(stock['Close'], fastperiod=6, slowperiod=12, signalperiod=9)
    ret = pd.concat([ret, stock['Close']], axis=1)
    
    ### 開始畫圖 ###
    ret.plot(color=color, linestyle='dashed')
    ret['Close'].plot(secondary_y=True, color=color[5])
    plt.title('MACD')  # 標題設定
    plt.grid(True, axis='y')
    plt.savefig('MACD.png')  # 存檔
    plt.close()  # 刪除記憶體中的圖片
    
    return Imgur.showImgur('MACD')

# 其他函數保持不變（若需使用，可類似更新移除 plt.show()）
