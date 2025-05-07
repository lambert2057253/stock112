import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import datetime
import Imgur
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties  # 字體管理模組，用於設定中文字體
import numpy as np

# 設定中文字體
chinese_font = matplotlib.font_manager.FontProperties(fname='msjh.ttf')

# 從 Yahoo Finance 獲取股票名稱
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

# 自定義 K 線圖繪製函數
def plot_kline(ax, data, stock_name):
    """繪製 K 線圖到指定的 Axes"""
    x = np.arange(len(data))
    width = 0.4  # 蠟燭寬度
    # 繪製蠟燭
    for i in range(len(data)):
        open_price = data['Open'].iloc[i]
        close_price = data['Close'].iloc[i]
        high_price = data['High'].iloc[i]
        low_price = data['Low'].iloc[i]
        color = 'red' if close_price >= open_price else 'green'
        # 繪製蠟燭主體
        ax.bar(i, abs(close_price - open_price), bottom=min(open_price, close_price), color=color, width=width)
        # 繪製上下影線
        ax.vlines(i, low_price, high_price, color=color, linewidth=1)

    ax.set_xticks(x[::20])  # 每 20 天顯示一個刻度
    ax.set_xticklabels(data.index[::20].strftime('%Y-%m-%d'), rotation=45, fontproperties=chinese_font)
    ax.set_ylabel('價格', fontproperties=chinese_font)
    ax.set_title(f'{stock_name} K 線圖', fontproperties=chinese_font, fontsize=16)
    ax.grid(True, alpha=0.3)

# 繪製並上傳獨立圖表
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
    
    print(f"[log:DEBUG] 數據形狀: {df.shape}")
    print(f"[log:DEBUG] 數據樣本: \n{df.tail(5)}")

    # 計算技術指標
    # 1. RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 2. MACD
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

    # 繪製三張獨立圖表
    # 1. K 線圖
    plt.figure(figsize=(12, 6))
    ax1 = plt.gca()
    plot_kline(ax1, df, stock_name)
    plt.savefig('kchart.png')
    plt.close()

    # 2. RSI 圖
    plt.figure(figsize=(12, 4))
    ax2 = plt.gca()
    ax2.plot(df['RSI'], label='RSI (14)', color='purple')
    ax2.axhline(70, linestyle='--', color='red', alpha=0.5)  # 超買線
    ax2.axhline(30, linestyle='--', color='green', alpha=0.5)  # 超賣線
    ax2.set_ylabel('RSI', fontproperties=chinese_font)
    ax2.set_title(f'{stock_name} RSI', fontproperties=chinese_font, fontsize=16)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(df.index[::20])
    ax2.set_xticklabels(df.index[::20].strftime('%Y-%m-%d'), rotation=45, fontproperties=chinese_font)
    ax2.legend(fontsize=10, prop=chinese_font)
    plt.savefig('rsi.png')
    plt.close()

    # 3. MACD 圖
    plt.figure(figsize=(12, 4))
    ax3 = plt.gca()
    ax3.plot(df['MACD'], label='MACD', color='blue')
    ax3.plot(df['Signal'], label='訊號線', color='red')
    ax3.bar(df.index, df['MACD_Hist'], color='gray', alpha=0.5)
    ax3.set_ylabel('MACD', fontproperties=chinese_font)
    ax3.set_title(f'{stock_name} MACD', fontproperties=chinese_font, fontsize=16)
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(df.index[::20])
    ax3.set_xticklabels(df.index[::20].strftime('%Y-%m-%d'), rotation=45, fontproperties=chinese_font)
    ax3.legend(fontsize=10, prop=chinese_font)
    plt.savefig('macd.png')
    plt.close()

    # 檢查圖表檔案並上傳
    for chart_file in ['kchart.png', 'rsi.png', 'macd.png']:
        if not os.path.exists(chart_file) or os.path.getsize(chart_file) == 0:
            print(f"[log:ERROR] {chart_file} 為空或未創建!")
            return f"{chart_file} 生成失敗，請稍後再試!"
    
    print(f"[log:INFO] 圖表已保存: kchart.png, rsi.png, macd.png")
    img_urls = {}
    for chart_file in ['kchart', 'rsi', 'macd']:
        img_url = Imgur.showImgur(f"{chart_file}")
        if not img_url.startswith("https"):
            print(f"[log:ERROR] Imgur 上傳 {chart_file}.png 失敗: {img_url}")
            return f"{chart_file}.png 上傳失敗，請稍後再試!"
        img_urls[chart_file] = img_url
        print(f"[log:INFO] {chart_file}.png 已上傳: {img_url}")
