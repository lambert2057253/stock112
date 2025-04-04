# kchart.py
import numpy as np
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup
import datetime
import pandas_ta as ta  # 替換 talib
from matplotlib.font_manager import FontProperties
import Imgur

# 設定中文字體
chinese_font = FontProperties(fname='msjh.ttf')
chinese_title = FontProperties(fname='msjh.ttf', size=24)
chinese_subtitle = FontProperties(fname='msjh.ttf', size=20)

def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/q/q?s={stockNumber}'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find_all(text='成交')[0].parent.parent.parent
        stock_name = table.select('tr')[1].select('td')[0].text.strip('加到投資組合')
        return stock_name
    except:
        return "no"

def draw_kchart(stockNumber):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365)
    stock = yf.Ticker(stockNumber + '.TW')
    df = stock.history(start=start, end=end)
    if df.empty:
        return "無法獲取股票數據!"

    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
    
    # 使用 pandas-ta 計算技術指標
    df['sma_5'] = ta.sma(df['Close'], length=5)
    df['sma_10'] = ta.sma(df['Close'], length=10)
    df['sma_20'] = ta.sma(df['Close'], length=20)
    df['sma_60'] = ta.sma(df['Close'], length=60)
    stoch = ta.stoch(df['High'], df['Low'], df['Close'])
    df['k'] = stoch['STOCHk_9_3_3']
    df['d'] = stoch['STOCHd_9_3_3']
    df['k'].fillna(value=0, inplace=True)
    df['d'].fillna(value=0, inplace=True)

    # 設定圖表樣式
    apds = [
        mpf.make_addplot(df['sma_5'], color='blue', label='5日均線'),
        mpf.make_addplot(df['sma_10'], color='orange', label='10日均線'),
        mpf.make_addplot(df['sma_20'], color='green', label='20日均線'),
        mpf.make_addplot(df['sma_60'], color='purple', label='60日均線'),
        mpf.make_addplot(df['k'], panel=1, color='red', label='K值'),
        mpf.make_addplot(df['d'], panel=1, color='blue', label='D值'),
    ]

    # 繪製 K 線圖
    fig, axes = mpf.plot(
        df, type='candle', style='charles', title=f'{stock_name} K線圖',
        ylabel='價格', volume=True, addplot=apds, panel_ratios=(1, 0.5, 0.5),
        savefig='kchart.png', returnfig=True
    )
    
    # 添加標題資訊
    axes[0].set_title(
        f"開盤價: {df['Open'].iloc[-1]:.2f} 收盤價: {df['Close'].iloc[-1]:.2f}\n"
        f"最高價: {df['High'].iloc[-1]:.2f} 最低價: {df['Low'].iloc[-1]:.2f}\n"
        f"更新日期: {df.index[-1]}",
        fontproperties=chinese_subtitle, loc='left', bbox=dict(facecolor='yellow', edgecolor='red', alpha=0.65)
    )
    
    # 保存並關閉圖表
    plt.savefig('kchart.png', bbox_inches='tight', dpi=300, pad_inches=0.0)
    plt.close(fig)

    # 上傳到 Imgur
    return Imgur.showImgur("kchart")
