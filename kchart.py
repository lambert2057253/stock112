import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import datetime
import Imgur
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

chinese_font = matplotlib.font_manager.FontProperties(fname='msjh.ttf')

def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/quote/{stockNumber}.TW'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page = requests.get(url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
        stock_name = soup.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)')
        if stock_name:
            return stock_name.text.strip()
        print(f"[log:WARNING] 找不到 {stockNumber} 的股票名稱")
        return "no"
    except Exception as e:
        print(f"[log:ERROR] 獲取 {stockNumber} 的股票名稱失敗: {e}")
        return "no"

def plot_kline(data, stock_name):
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(data))
    width = 0.4
    for i in range(len(data)):
        open_price = data['Open'].iloc[i]
        close_price = data['Close'].iloc[i]
        high_price = data['High'].iloc[i]
        low_price = data['Low'].iloc[i]
        color = 'red' if close_price >= open_price else 'green'
        ax.bar(i, abs(close_price - open_price), bottom=min(open_price, close_price), color=color, width=width)
        ax.vlines(i, low_price, high_price, color=color, linewidth=1)

    ax.set_xticks(x[::20])
    ax.set_xticklabels(data.index[::20].strftime('%Y-%m-%d'), rotation=45, fontproperties=chinese_font)
    ax.set_ylabel('價格', fontproperties=chinese_font)
    ax.set_title(f'{stock_name} K線圖', fontproperties=chinese_font, fontsize=16)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('kchart_kline.png')
    plt.close()

def plot_rsi(data):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(data['RSI'], label='RSI (14)', color='purple')
    ax.axhline(70, linestyle='--', color='red', alpha=0.5)
    ax.axhline(30, linestyle='--', color='green', alpha=0.5)
    ax.set_ylabel('RSI', fontproperties=chinese_font)
    ax.set_title('RSI', fontproperties=chinese_font, fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('kchart_rsi.png')
    plt.close()

def plot_macd(data):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(data['MACD'], label='MACD', color='blue')
    ax.plot(data['Signal'], label='訊號線', color='red')
    ax.bar(data.index, data['MACD_Hist'], color='gray', alpha=0.5)
    ax.set_ylabel('MACD', fontproperties=chinese_font)
    ax.set_title('MACD', fontproperties=chinese_font, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, prop=chinese_font)
    plt.tight_layout()
    plt.savefig('kchart_macd.png')
    plt.close()

def draw_kchart(stockNumber):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365)
    stock = yf.Ticker(stockNumber + '.TW')
    df = stock.history(start=start, end=end)
    if df.empty:
        print(f"[log:ERROR] 無法獲取 {stockNumber}.TW 的數據")
        return "無法獲取股票數據!"
    
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

    plot_kline(df, stock_name)
    plot_rsi(df)
    plot_macd(df)

    urls = []
    for img in ['kchart_kline', 'kchart_rsi', 'kchart_macd']:
        if not os.path.exists(f'{img}.png'):
            print(f"[log:ERROR] {img}.png 圖片未建立")
            return "圖表產生失敗"
        url = Imgur.showImgur(img)
        if not url.startswith("https"):
            print(f"[log:ERROR] Imgur 上傳失敗: {url}")
            return "圖片上傳失敗"
        urls.append(url)

    return urls
