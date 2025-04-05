# Technical_Analysis.py
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import talib
from talib import abstract
import Imgur
import matplotlib.pyplot as plt
import pandas_datareader as pdr
import requests
import datetime
from bs4 import BeautifulSoup
from matplotlib.font_manager import FontProperties
import os

# 固定字體路徑
font_path = '/opt/render/project/src/msjh.ttf'
if not os.path.exists(font_path):
    print(f"[log:ERROR] Font file {font_path} not found! Using default font.")
    chinese_font = FontProperties()
else:
    print(f"[log:INFO] Font file {font_path} found.")
    chinese_font = FontProperties(fname=font_path)

def general_df(stockNumber):
    stockNumberTW = stockNumber + ".TW"
    df_x = pdr.DataReader(stockNumberTW, 'yahoo', start="2019")
    df_x.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)
    return df_x

def get_stockName(stockNumber):
    url = 'https://tw.stock.yahoo.com/q/q?s=' + stockNumber
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all(text='成交')[0].parent.parent.parent
    stock_name = table.select('tr')[1].select('td')[0].text
    stock_name = stock_name.strip('加到投資組合')
    return stock_name

def MACD_pic(stockNumber, msg):
    stock_name = get_stockName(stockNumber)
    df_x = general_df(stockNumber)
    jj = df_x.reset_index(drop=False)
    abstract.MACD(df_x).plot(figsize=(16, 8))
    plt.xlabel("日期", fontproperties=chinese_font)
    plt.ylabel("值", fontproperties=chinese_font)
    plt.grid(True, axis='y')
    plt.title(stock_name + " MACD線", fontproperties=chinese_font)
    plt.savefig(msg + ".png")
    plt.close()
    return Imgur.showImgur(msg)

def RSI_pic(stockNumber, msg):
    stock_name = get_stockName(stockNumber)
    df_x = general_df(stockNumber)
    jj = df_x.reset_index(drop=False)
    abstract.RSI(df_x).plot(figsize=(16, 8))
    plt.xlabel("日期", fontproperties=chinese_font)
    plt.ylabel("KD值", fontproperties=chinese_font)
    plt.grid(True, axis='y')
    plt.title(stock_name + " KD線", fontproperties=chinese_font)
    plt.savefig(msg + ".png")
    plt.close()
    return Imgur.showImgur(msg)

def BBANDS_pic(stockNumber, msg):
    stock_name = get_stockName(stockNumber)
    df_x = general_df(stockNumber)
    jj = df_x.reset_index(drop=False)
    abstract.BBANDS(df_x).plot(figsize=(16, 8))
    plt.xlabel("日期", fontproperties=chinese_font)
    plt.ylabel("價格", fontproperties=chinese_font)
    plt.grid(True, axis='y')
    plt.title(stock_name + " BBANDS", fontproperties=chinese_font)
    plt.savefig(msg + ".png")
    plt.close()
    return Imgur.showImgur(msg)
