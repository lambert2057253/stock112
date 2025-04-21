''' 
即時股價與走勢圖
'''
import requests  # HTTP請求庫，用於從網路上抓取資料
import datetime  # 日期時間處理庫，用於日期計算
import pandas as pd  # 資料處理庫，用於表格數據操作
import yfinance as yf  # Yahoo Finance API，用於獲取股票歷史數據
from bs4 import BeautifulSoup  # HTML解析庫，用於提取網頁內容
import Imgur  # 自定義模組
import matplotlib  # 繪圖基礎庫
import matplotlib.pyplot as plt  # Matplotlib的子模組，用於繪圖
from matplotlib.font_manager import FontProperties  # 字體管理模組，用於設定中文字體

# 設定中文字體
chinese_font = matplotlib.font_manager.FontProperties(fname='msjh.ttf')  # 引入同個資料夾下的微軟正黑體字體檔案

# Emoji 定義，用於美化輸出訊息
emoji_upinfo = u'\U0001F447'  # 向下箭頭
emoji_midinfo = u'\U0001F538'  # 小橘色圓點
emoji_downinfo = u'\U0001F60A'  # 笑臉

# 從 Yahoo Finance 獲取股票名稱
def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/quote/{stockNumber}.TW'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        stock_name = soup.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)').text
        return stock_name
    except Exception as e:
        print(f"[log:ERROR] Error in get_stock_name: {e}")
        return "no"

# 查詢股票即時資訊
def getprice(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"
    content = ""
    stock = yf.Ticker(stockNumber + '.TW')
    hist = stock.history(period="5d")
    if hist.empty:
        return "無法獲取股票數據，請確認代碼或稍後再試!"
    
    date = hist.index[-1].strftime('%Y-%m-%d')
    price = '%.2f' % hist["Close"].iloc[-1]
    last_price = '%.2f' % hist["Close"].iloc[-2]
    spread_price = '%.2f' % (float(price) - float(last_price))
    spread_ratio = '%.2f' % (float(spread_price) / float(last_price) * 100) + '%'
    spread_price = spread_price.replace("-", "▽ ") if float(last_price) > float(price) else "△ " + spread_price
    spread_ratio = spread_ratio.replace("-", "▽ ") if float(last_price) > float(price) else "△ " + spread_ratio
    open_price = '%.2f' % hist["Open"].iloc[-1]
    high_price = '%.2f' % hist["High"].iloc[-1]
    low_price = '%.2f' % hist["Low"].iloc[-1]
    price_five = hist["Close"].iloc[-5:]
    stockAverage = '%.2f' % price_five.mean()
    stockSTD = '%.2f' % price_five.std()
    
    content += f"{stock_name} 股票報告{emoji_upinfo}\n--------------\n日期: {date}\n{emoji_midinfo}最新收盤價: {price}\n{emoji_midinfo}開盤價: {open_price}\n{emoji_midinfo}最高價: {high_price}\n{emoji_midinfo}最低價: {low_price}\n{emoji_midinfo}漲跌價差: {spread_price} 漲跌幅: {spread_ratio}\n{emoji_midinfo}五日平均價格: {stockAverage}\n{emoji_midinfo}五日標準差: {stockSTD}\n"
    if msg.startswith("#"):
        content += f"--------------\n請選擇下方選項查看更多詳情{emoji_downinfo}"
    else:
        content += '\n'
    return content

# 繪製近一年股價走勢圖（加入 SMA 和 MACD）
def stock_trend(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"

    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    
    stock = yf.Ticker(stockNumber + '.TW')
    stock_data = stock.history(start=f"{year}-{month}-01", end=end)
    
    if stock_data.empty:
        print(f"[log:ERROR] No trend data for {stockNumber}.TW")
        return "no"
    
    # 計算技術指標
    stock_data['SMA10'] = stock_data['Close'].rolling(window=10).mean()  # 10日均線
    stock_data['SMA50'] = stock_data['Close'].rolling(window=50).mean()  # 50日均線
    stock_data['EMA12'] = stock_data['Close'].ewm(span=12, adjust=False).mean()  # 12日EMA
    stock_data['EMA26'] = stock_data['Close'].ewm(span=26, adjust=False).mean()  # 26日EMA
    stock_data['MACD'] = stock_data['EMA12'] - stock_data['EMA26']  # MACD線
    stock_data['Signal'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()  # 訊號線

    # 繪製圖表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 主圖：價格與均線
    ax1.plot(stock_data["Close"], '-', label="收盤價", color='blue')
    ax1.plot(stock_data["High"], '-', label="最高價", color='green', alpha=0.5)
    ax1.plot(stock_data["Low"], '-', label="最低價", color='red', alpha=0.5)
    ax1.plot(stock_data["SMA10"], '-', label="10日均線", color='orange')
    ax1.plot(stock_data["SMA50"], '-', label="50日均線", color='purple')
    ax1.set_title(f'{stock_name} 近一年價格走勢', fontsize=20, fontproperties=chinese_font)
    ax1.set_xlabel('日期', fontsize=14, fontproperties=chinese_font)
    ax1.set_ylabel('價格', fontsize=14, fontproperties=chinese_font)
    ax1.grid(True)
    ax1.legend(fontsize=12, prop=chinese_font)

    # 副圖：MACD
    ax2.plot(stock_data['MACD'], label='MACD', color='blue')
    ax2.plot(stock_data['Signal'], label='訊號線', color='red')
    ax2.fill_between(stock_data.index, stock_data['MACD'] - stock_data['Signal'], alpha=0.3, color='gray')
    ax2.set_title('MACD', fontsize=14, fontproperties=chinese_font)
    ax2.set_xlabel('日期', fontsize=14, fontproperties=chinese_font)
    ax2.set_ylabel('MACD', fontsize=14, fontproperties=chinese_font)
    ax2.grid(True)
    ax2.legend(fontsize=12, prop=chinese_font)

    plt.tight_layout()
    plt.savefig(msg + '.png')
    plt.close()
    return Imgur.showImgur(msg)

# 繪製近一年股票收益率走勢圖（加入移動平均收益率和標準差）
def show_return(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"

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
    
    # 計算技術指標
    stock_data['Return_MA20'] = stock_data['Returns'].rolling(window=20).mean()  # 20日均收益率
    stock_data['Return_Std20'] = stock_data['Returns'].rolling(window=20).std()  # 20日標準差

    # 繪製圖表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 主圖：收益率與移動平均
    ax1.plot(stock_return, label="日收益率", color='blue')
    ax1.plot(stock_data['Return_MA20'], label="20日均收益率", color='orange')
    ax1.set_title(f'{stock_name} 近一年收益率走勢', fontsize=20, fontproperties=chinese_font)
    ax1.set_xlabel('日期', fontsize=14, fontproperties=chinese_font)
    ax1.set_ylabel('收益率', fontsize=14, fontproperties=chinese_font)
    ax1.grid(True)
    ax1.legend(fontsize=12, prop=chinese_font)

    # 副圖：標準差
    ax2.plot(stock_data['Return_Std20'], label="20日標準差", color='purple')
    ax2.set_title('收益率波動性', fontsize=14, fontproperties=chinese_font)
    ax2.set_xlabel('日期', fontsize=14, fontproperties=chinese_font)
    ax2.set_ylabel('標準差', fontsize=14, fontproperties=chinese_font)
    ax2.grid(True)
    ax2.legend(fontsize=12, prop=chinese_font)

    plt.tight_layout()
    plt.savefig(msg + '.png')
    plt.close()
    return Imgur.showImgur(msg)

# 繪製近一年股價Shock盪圖（加入移動平均震盪幅度和標準差）
def show_fluctuation(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no":
        return "股票代碼錯誤!"

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
    
    # 計算技術指標
    stock_data['Fluctuation_MA20'] = stock_data['stock_fluctuation'].rolling(window=20).mean()  # 20日均震盪幅度
    stock_data['Fluctuation_Std20'] = stock_data['stock_fluctuation'].rolling(window=20).std()  # 20日標準差

    # 繪製圖表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
    
    # 主圖：震盪幅度與移動平均
    ax1.plot(stock_data['stock_fluctuation'], '-', label="日震盪幅度", color='orange')
    ax1.plot(stock_data['Fluctuation_MA20'], '-', label="20日均震盪幅度", color='blue')
    ax1.set_title(f'{stock_name} 近一年價格震盪', fontsize=20, fontproperties=chinese_font)
    ax1.set_xlabel('日期', fontsize=14, fontproperties=chinese_font)
    ax1.set_ylabel('價格', fontsize=14, fontproperties=chinese_font)
    ax1.grid(True)
    ax1.legend(fontsize=12, prop=chinese_font)

    # 副圖：標準差
    ax2.plot(stock_data['Fluctuation_Std20'], label="20日標準差", color='purple')
    ax2.set_title('震盪幅度波動性', fontsize=14, fontproperties=chinese_font)
    ax2.set_xlabel('日期', fontsize=14, fontproperties=chinese_font)
    ax2.set_ylabel('標準差', fontsize=14, fontproperties=chinese_font)
    ax2.grid(True)
    ax2.legend(fontsize=12, prop=chinese_font)

    plt.tight_layout()
    plt.savefig(msg + '.png')
    plt.close()
    return Imgur.showImgur(msg)
