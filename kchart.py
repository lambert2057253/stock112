# kchart.py
import numpy as np
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import requests
from bs4 import BeautifulSoup
import datetime
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import Imgur
import os

# 動態生成字體路徑
font_path = os.path.join(os.path.dirname(__file__), 'msjh.ttf')
if not os.path.exists(font_path):
    print(f"[log:ERROR] Font file {font_path} not found! Using default font.")
    chinese_font = FontProperties()
    chinese_title = FontProperties(size=24)
    chinese_subtitle = FontProperties(size=20)
else:
    print(f"[log:INFO] Font file {font_path} found.")
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
    
    print(f"[log:DEBUG] Data shape: {df.shape}")
    print(f"[log:DEBUG] Data sample: \n{df.tail(5)}")

    # 繪製圖表
    print("[log:INFO] Starting chart generation")
    mpf.plot(
        df, type='candle', style='charles', title=f'{stock_name} K線圖',
        ylabel='價格', volume=True, mav=(5, 10, 20, 60), savefig='kchart.png'
    )
    
    if not os.path.exists('kchart.png') or os.path.getsize('kchart.png') == 0:
        print("[log:ERROR] kchart.png is empty or not created!")
        return "圖表生成失敗，請稍後再試！"
    
    print("[log:INFO] Chart saved to kchart.png")
    img_url = Imgur.showImgur("kchart")
    if not img_url.startswith("https"):
        print(f"[log:ERROR] Imgur upload failed: {img_url}")
        return "圖片上傳失敗，請稍後再試！"
    print(f"[log:INFO] Chart uploaded: {img_url}")
    return img_url
