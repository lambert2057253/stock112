# kchart.py
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup
import datetime
import Imgur
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 設定中文字體，與 stockprice.py 一致
chinese_font = matplotlib.font_manager.FontProperties(fname='msjh.ttf') # 引入同個資料夾下支援中文字檔

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
    stock = yf.Ticker(stockNumber + '.TW')
    df = stock.history(start=start, end=end)
    if df.empty:
        print(f"[log:ERROR] No data returned for {stockNumber}.TW")
        return "無法獲取股票數據!"
    
    print(f"[log:DEBUG] 數據形狀: {df.shape}")
    print(f"[log:DEBUG] 數據樣本: \n{df.tail(5)}")

    print("[log:INFO] 開始生成圖表")
    
    # 使用 mplfinance 繪製 K 線圖
    fig, ax = plt.subplots(figsize=(12, 6))
    mpf.plot(
        df,
        type='candle',
        style='charles',
        title=f'{stock_name} K線圖',
        ylabel='價格',
        volume=ax2,  
        mav=(5, 10, 20, 60),
        ax=ax1,
        tight_layout=True
    )
    
    # 添加額外的中文標題和標籤，與 stockprice.py 一致
    ax.set_title(
        f"開盤價: {round(df['Open'][-1], 2)} 收盤價: {round(df['Close'][-1], 2)} "
        f"最高價: {round(df['High'][-1], 2)} 最低價: {round(df['Low'][-1], 2)}",
        fontsize=12, fontweight='bold', loc='left', fontproperties=chinese_font
    )
    ax.set_xlabel(f"更新日期: {df.index[-1].strftime('%Y-%m-%d')}", fontsize=12, fontproperties=chinese_font)
    
    # 保存圖表
    plt.savefig("Kchart.png", bbox_inches='tight', dpi=100, pad_inches=0.1)
    plt.close()
    
    # 上傳至 Imgur
    img_url = Imgur.showImgur("Kchart")
    if not img_url.startswith("https"):
        print(f"[log:ERROR] Imgur 上傳失敗: {img_url}")
        return "圖片上傳失敗，請稍後再試!"
    print(f"[log:INFO] 圖表已上傳: {img_url}")
    return img_url
