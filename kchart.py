# kchart.py
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import datetime
import Imgur
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import mplfinance as mpf

# 設定中文字體
font_path = 'msjh.ttf'
chinese_font = FontProperties(fname=font_path)
chinese_title = FontProperties(fname=font_path, size=16)
chinese_subtitle = FontProperties(fname=font_path, size=12)

def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/quote/{stockNumber}.TW'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        page = requests.get(url, headers=headers, timeout=10)
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
        
        # 計算移動平均線 (SMA)
        hist['SMA5'] = hist['Close'].rolling(window=5).mean()
        hist['SMA10'] = hist['Close'].rolling(window=10).mean()
        hist['SMA20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA60'] = hist['Close'].rolling(window=60).mean()
        
        # 繪製 K 線圖
        fig, ax = plt.subplots(figsize=(12, 6))  # 減小圖表尺寸
        mpf.plot(
            hist,
            type='candle',
            style='charles',
            title=f"{stock_name} K線圖",
            ylabel='價格',
            mav=(5, 10, 20, 60),
            ax=ax,
            tight_layout=True,
            fontfamily='Microsoft JhengHei'  # 使用系統內建中文字體
        )
        ax.set_title(
            f"開盤價: {round(hist['Open'][-1], 2)} 收盤價: {round(hist['Close'][-1], 2)} "
            f"最高價: {round(hist['High'][-1], 2)} 最低價: {round(hist['Low'][-1], 2)}",
            fontsize=12, fontweight='bold', loc='left', fontproperties=chinese_subtitle
        )
        ax.set_xlabel(f"更新日期: {hist.index[-1].strftime('%Y-%m-%d')}", fontsize=12, fontproperties=chinese_subtitle)
        
        # 保存圖表
        plt.savefig("Kchart.png", bbox_inches='tight', dpi=100, pad_inches=0.1)  # 降低 DPI
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
