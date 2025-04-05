'''
emoji編碼列表：
https://apps.timwhitlock.info/emoji/tables/unicode#block-6c-other-additional-symbols
'''
import requests
from bs4 import BeautifulSoup

happy = u'\U0001F604'  # emoji 需以unicode進行編碼 (源碼: U+1F604)
emoji_list = [u'\U0001F4D5', u'\U0001F606']

# 個股新聞
def get_single_stock_news(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/q/h?s={stockNumber}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[log:ERROR] Failed to fetch page for {stockNumber}: HTTP {response.status_code}")
            return ["無法獲取新聞"], []
        
        sp = BeautifulSoup(response.text, "html.parser")
        tables = sp.find_all('table')
        if len(tables) < 3:
            print(f"[log:ERROR] Insufficient tables found for {stockNumber}, got {len(tables)}")
            return ["無法獲取新聞"], []
        
        table = tables[2]  # 第 3 個表格
        links = table.find_all('a')
        if len(links) < 6:  # 確保至少有 6 個連結（1 跳過 + 5 新聞）
            print(f"[log:ERROR] Insufficient links found in table for {stockNumber}, got {len(links)}")
            return ["無法獲取足夠的新聞"], []
        
        title_list = []
        url_list = []
        for i in range(1, 6):  # 前五則消息
            trs = links[i]
            title = trs.text.strip()
            if len(title) > 20:
                title = title[0:20]
            title_list.append(title)
            url_list.append(trs.get("href"))
        
        return title_list, url_list
    except Exception as e:
        print(f"[log:ERROR] Error fetching news for {stockNumber}: {e}")
        return ["無法獲取新聞"], []

# 鉅亨網新聞(外幣匯率新聞)
def anue_forex_news():
    try:
        url = requests.get('https://news.cnyes.com/news/cat/forex')
        sp1 = BeautifulSoup(url.text, "html.parser")
        title_list = []
        url_list = []
        articles = sp1.find_all('a', class_='_1Zdp')
        if len(articles) < 5:
            print(f"[log:ERROR] Insufficient articles found for forex news, got {len(articles)}")
            return ["無法獲取外幣匯率新聞"], []
        
        for i in range(0, 5):
            article = articles[i]
            url_list.append('https://news.cnyes.com' + article.get('href'))
            title = article.get('title')
            if len(title) > 20:
                title = title[0:20]
            title_list.append(title)
        return title_list, url_list
    except Exception as e:
        print(f"[log:ERROR] Error fetching forex news: {e}")
        return ["無法獲取外幣匯率新聞"], []

# 鉅亨網新聞(頭條新聞)
def anue_headline_news():
    try:
        url2 = requests.get('https://news.cnyes.com/news/cat/headline')
        sp2 = BeautifulSoup(url2.text, "html.parser")
        articles = sp2.find_all('a', class_='_1Zdp')
        if len(articles) < 5:
            print(f"[log:ERROR] Insufficient articles found for headline news, got {len(articles)}")
            return "無法獲取頭條新聞"
        
        content = ''
        for i in range(0, 5):
            article = articles[i]
            href2 = article.get('href')
            title2 = article.get('title')
            content += title2 + '\n' + 'https://news.cnyes.com' + href2 + '\n ------ \n'
        return content
    except Exception as e:
        print(f"[log:ERROR] Error fetching headline news: {e}")
        return "無法獲取頭條新聞"

# 每周財經大事新聞
def weekly_news():
    try:
        url3 = requests.get('https://pocketmoney.tw/articles/')
        sp3 = BeautifulSoup(url3.text, "html.parser")
        images = sp3.find_all('img', class_="wp-post-image")
        links = sp3.find_all('a', class_='post-thumb')
        if not images or not links:
            print(f"[log:ERROR] No image or link found for weekly news")
            return "無法獲取圖片", "無法獲取連結"
        
        get_img = images[0]
        table3 = links[0]
        href3 = table3.get('href')
        img3 = get_img.get("src")
        return img3, href3
    except Exception as e:
        print(f"[log:ERROR] Error fetching weekly news: {e}")
        return "無法獲取圖片", "無法獲取連結"

# 台股盤勢(yahoo)
def twStock_news():
    try:
        url = requests.get('https://tw.stock.yahoo.com/news_list/url/d/e/N2.html')
        sp = BeautifulSoup(url.text, "html.parser")
        links = sp.find_all("a", class_='mbody')
        if len(links) < 10:
            print(f"[log:ERROR] Insufficient links found for twStock news, got {len(links)}")
            return "無法獲取台股盤勢新聞"
        
        content = ""
        for i in range(1, 10, 2):
            table = links[i]
            href = table.get("href")
            content += emoji_list[0] + href + '\n \n'
        return content
    except Exception as e:
        print(f"[log:ERROR] Error fetching twStock news: {e}")
        return "無法獲取台股盤勢新聞"

# 股市重大要聞(yahoo)
def important_news():
    try:
        url1 = requests.get('https://tw.stock.yahoo.com/news_list/url/d/e/N1.html')
        sp1 = BeautifulSoup(url1.text, "html.parser")
        links = sp1.find_all("a", class_='mbody')
        if len(links) < 10:
            print(f"[log:ERROR] Insufficient links found for important news, got {len(links)}")
            return "無法獲取股市重大要聞"
        
        content = ""
        for i in range(1, 10, 2):
            table1 = links[i]
            href1 = table1.get("href")
            content += happy + href1 + '\n \n'
        return content
    except Exception as e:
        print(f"[log:ERROR] Error fetching important news: {e}")
        return "無法獲取股市重大要聞"

# 鉅亨網新聞(台灣政經新聞)
def anue_news():
    try:
        news_url = requests.get('https://news.cnyes.com/news/cat/tw_macro')
        sp2 = BeautifulSoup(news_url.text, "html.parser")
        articles = sp2.find_all('a', class_='_1Zdp')
        if len(articles) < 5:
            print(f"[log:ERROR] Insufficient articles found for anue news, got {len(articles)}")
            return "無法獲取台灣政經新聞"
        
        content = ""
        for i in range(0, 5):
            article = articles[i]
            href2 = article.get('href')
            title2 = article.get('title')
            content += title2 + '\n' + href2 + '\n ------ \n'
        return content
    except Exception as e:
        print(f"[log:ERROR] Error fetching anue news: {e}")
        return "無法獲取台灣政經新聞"
