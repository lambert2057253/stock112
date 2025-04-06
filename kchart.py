# kchart.py
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import datetime
import Imgur
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 設定中文字體
font_path = 'msjh.ttf'
chinese_font = FontProperties(fname=font_path)
chinese_title = FontProperties(fname=font_path, size=24)
chinese_subtitle = FontProperties(fname=font_path, size=20)

def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/quote/{stockNumber}.TW'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        page = requests.get(url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')
        stock_name = soup.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)')
        if stock_name:
            return stock_name.text.strip()
        print(f"[log:WARNING] No stock name found for {stockNumber}")
        return "no"
    except Exception as e:
        print(f"[log:ERROR] Failed to get stock name for {stockNumber}: {e}")
        return "no"

def draw_kchart(stockNumber):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365)
    
    try:
        # 使用 yfinance 獲取數據
        stock = yf.Ticker(stockNumber + '.TW')
        hist = stock.history(start=start, end=end)
        if hist.empty:
            print(f"[log:ERROR] No data returned for {stockNumber}.TW")
            return "無法獲取股票數據，請稍後再試！"
        
        hist.index = hist.index.strftime('%Y-%m-%d')
        
        # 計算移動平均線 (SMA)
        sma_5 = hist['Close'].rolling(window=5).mean()
        sma_10 = hist['Close'].rolling(window=10).mean()
        sma_20 = hist['Close'].rolling(window=20).mean()
        sma_60 = hist['Close'].rolling(window=60).mean()
        
        # 計算 KD 值 (Stochastic Oscillator)
        low_min = hist['Low'].rolling(window=9).min()
        high_max = hist['High'].rolling(window=9).max()
        hist['k'] = 100 * (hist['Close'] - low_min) / (high_max - low_min)
        hist['d'] = hist['k'].rolling(window=3).mean()
        hist['k'].fillna(value=0, inplace=True)
        hist['d'].fillna(value=0, inplace=True)
        
        # 繪製圖表
        fig = plt.figure(figsize=(20, 10))
        fig.suptitle(stock_name, fontsize="x-large", fontproperties=chinese_title)
        
        # K 線圖和均線
        ax = fig.add_axes([0.1, 0.5, 0.75, 0.4])
        plt.title(
            f"開盤價: {round(hist['Open'][-1], 2)}  收盤價: {round(hist['Close'][-1], 2)}\n"
            f"最高價: {round(hist['High'][-1], 2)}  最低價: {round(hist['Low'][-1], 2)}",
            fontsize=25, fontweight='bold', bbox=dict(facecolor='yellow', edgecolor='red', alpha=0.65),
            loc='left', fontproperties=chinese_subtitle
        )
        plt.title(f"更新日期: {hist.index[-1]}", fontsize=20, fontweight='bold', loc="right", fontproperties=chinese_subtitle)
        plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
        
        # 手動繪製 K 線
        for i in range(len(hist)):
            open_price = hist['Open'].iloc[i]
            close_price = hist['Close'].iloc[i]
            high_price = hist['High'].iloc[i]
            low_price = hist['Low'].iloc[i]
            color = 'r' if close_price >= open_price else 'g'
            ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)
            ax.plot([i, i], [open_price, close_price], color=color, linewidth=3)
        
        ax.plot(sma_5, label='5日均線', linestyle='--')
        ax.plot(sma_10, label='10日均線', linestyle='--')
        ax.plot(sma_20, label='20日均線', linestyle='--')
        ax.plot(sma_60, label='60日均線', linestyle='--')
        
        # KD 圖
        ax2 = fig.add_axes([0.1, 0.3, 0.75, 0.20])
        ax2.plot(hist['k'], label='K值', linestyle='-', color='b')
        ax2.plot(hist['d'], label='D值', linestyle='-', color='orange')
        ax2.set_xticks(range(0, len(hist.index), 10))
        ax2.set_xticklabels(hist.index[::10], fontsize=10, rotation=25)
        plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
        
        # 成交量圖
        ax3 = fig.add_axes([0.1, 0.03, 0.75, 0.20])
        for i in range(len(hist)):
            open_price = hist['Open'].iloc[i]
            close_price = hist['Close'].iloc[i]
            volume = hist['Volume'].iloc[i]
            color = 'r' if close_price >= open_price else 'g'
            ax3.bar(i, volume, color=color, alpha=0.8, width=0.5)
        ax3.set_xticks(range(0, len(hist.index), 10))
        ax3.set_xticklabels(hist.index[::10], fontsize=10, rotation=45)  # 修正步長為 10
        plt.grid(True, linestyle="--", color='gray', linewidth='0.5', axis='both')
        
        # 設置圖例
        ax.legend(prop=chinese_font, fontsize=20)
        ax2.legend(prop=chinese_font)
        
        # 保存圖表
        plt.savefig("Kchart.png", bbox_inches='tight', dpi=300, pad_inches=0.0)
        plt.close()
        
        # 上傳至 Imgur
        img_url = Imgur.showImgur("Kchart")
        if not img_url.startswith("https"):
            print(f"[log:ERROR] Imgur upload failed: {img_url}")
            return "圖表上傳失敗，請稍後再試！"
        
        print(f"[log:INFO] Chart uploaded: {img_url}")
        return img_url
    
    except Exception as e:
        print(f"[log:ERROR] Error in draw_kchart for {stockNumber}: {e}")
        return "生成圖表時發生錯誤，請稍後再試！"
