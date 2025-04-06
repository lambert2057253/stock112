# -*- coding: utf-8 -*-
''' 
即時股價與走勢圖
'''
import requests
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from bs4 import BeautifulSoup
import Imgur
from matplotlib.font_manager import FontProperties # 設定字體
chinese_font = matplotlib.font_manager.FontProperties(fname='msjh.ttf') # 引入同個資料夾下支援中文字檔


emoji_upinfo = u'\U0001F447'
emoji_midinfo = u'\U0001F538'
emoji_downinfo = u'\U0001F60A'

def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/quote/{stockNumber}.TW'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        stock_name = soup.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)').text
        return stock_name
    except Exception as e:
        print(f"Error in get_stock_name: {e}")
        return "no"

# 使用者查詢股票
def getprice(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no": return "Invalid stock code!"
    content = ""
    stock = yf.Ticker(stockNumber + '.TW')
    hist = stock.history(period="5d")  # 獲取近5天的歷史數據
    if hist.empty: return "No stock data available, please check the code or try again later!"
    date = hist.index[-1].strftime('%Y-%m-%d')
    price = '%.2f' % hist["Close"].iloc[-1]  # 近日收盤價
    last_price = '%.2f' % hist["Close"].iloc[-2]  # 前一日收盤價
    spread_price = '%.2f' % (float(price) - float(last_price))  # 價差
    spread_ratio = '%.2f' % (float(spread_price) / float(last_price) * 100) + '%'  # 漲跌幅（百分比）
    spread_price = spread_price.replace("-", "▽ ") if float(last_price) > float(price) else "△ " + spread_price
    spread_ratio = spread_ratio.replace("-", "▽ ") if float(last_price) > float(price) else "△ " + spread_ratio
    open_price = '%.2f' % hist["Open"].iloc[-1]  # 開盤價
    high_price = '%.2f' % hist["High"].iloc[-1]  # 最高價
    low_price = '%.2f' % hist["Low"].iloc[-1]  # 最低價
    price_five = hist["Close"].iloc[-5:]  # 近五日收盤價
    stockAverage = '%.2f' % price_five.mean()  # 近五日平均價格
    stockSTD = '%.2f' % price_five.std()  # 近五日標準差
    content += f"Stock Report for {stock_name}{emoji_upinfo}\n--------------\nDate: {date}\n{emoji_midinfo}Latest Close: {price}\n{emoji_midinfo}Open: {open_price}\n{emoji_midinfo}High: {high_price}\n{emoji_midinfo}Low: {low_price}\n{emoji_midinfo}Change: {spread_price} Change %: {spread_ratio}\n{emoji_midinfo}5-Day Avg Price: {stockAverage}\n{emoji_midinfo}5-Day Std Dev: {stockSTD}\n"
    if msg.startswith("#"): content += f"--------------\nFor more details, select options below{emoji_downinfo}"
    else: 
        content += '\n'
    return content

# 畫近一年股價走勢圖
def stock_trend(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "Invalid stock code!"

    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    
    stock = yf.Ticker(stockNumber + '.TW')
    stock_data = stock.history(start=f"{year}-{month}-01", end=end)
    
    if stock_data.empty:
        print(f"[log:ERROR] No trend data for {stockNumber}.TW")
        return "no"
    
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data["Close"], '-', label="Close Price")
    plt.plot(stock_data["High"], '-', label="High Price")
    plt.plot(stock_data["Low"], '-', label="Low Price")
    plt.title(f'{stock_name} Annual Price Trend', loc='center', fontsize=20)
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.grid(True, axis='y')
    plt.legend(fontsize=14)
    plt.savefig(msg + '.png')
    plt.close()
    
    return Imgur.showImgur(msg)

# 股票收益率：代表股票在一天交易中的價值變化百分比
def show_return(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "Invalid stock code!"

    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    
    stock = yf.Ticker(stockNumber + '.TW')
    stock_data = stock.history(start=f"{year}-{month}-01", end=end)
    
    if stock_data.empty:
        print(f"[log:ERROR] No return data for {stockNumber}.TW")
        return "no"
    
    stock_data['Returns'] = stock_data['Close'].pct_change()
    stock_return = stock_data['Returns'].dropna()
    
    plt.figure(figsize=(12, 6))
    plt.plot(stock_return, label="Return Rate")
    plt.title(f'{stock_name} Annual Return Trend', loc='center', fontsize=20)
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('Return Rate', fontsize=20)
    plt.grid(True, axis='y')
    plt.legend(fontsize=14)
    plt.savefig(msg + '.png')
    plt.close()
    
    return Imgur.showImgur(msg)

# 畫股價震盪圖
def show_fluctuation(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "Invalid stock code!"

    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    
    stock = yf.Ticker(stockNumber + '.TW')
    stock_data = stock.history(start=f"{year}-{month}-01", end=end)
    
    if stock_data.empty:
        print(f"[log:ERROR] No fluctuation data for {stockNumber}.TW")
        return "no"
    
    stock_data['stock_fluctuation'] = stock_data["High"] - stock_data["Low"]
    
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['stock_fluctuation'], '-', label="Fluctuation", color="orange")
    plt.title(f'{stock_name} Annual Price Fluctuation', loc='center', fontsize=20)
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('Price', fontsize=20)
    plt.grid(True, axis='y')
    plt.legend(fontsize=14)
    plt.savefig(msg + '.png')
    plt.close()
    
    return Imgur.showImgur(msg)
