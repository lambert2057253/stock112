'''
Upload pics
'''
import matplotlib
matplotlib.use('Agg')  # 確保非 GUI 環境下運行
from imgurpython import ImgurClient
import os
import datetime

def showImgur(fileName):
    # 從環境變數獲取 Imgur 憑證
    client_id = os.getenv('IMGUR_CLIENT_ID')
    client_secret = os.getenv('IMGUR_CLIENT_SECRET')
    album_id = os.getenv('IMGUR_ALBUM_ID')
    access_token = os.getenv('IMGUR_ACCESS_TOKEN')
    refresh_token = os.getenv('IMGUR_REFRESH_TOKEN')

    # 連接到 Imgur
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    
    # 配置參數
    config = {
        'album': album_id,
        'name': fileName,
        'title': fileName,
        'description': str(datetime.date.today())
    }
    
    # 上傳檔案
    try:
        print(f"[log:INFO] Uploading image: {fileName}.png")
        imgurl = client.upload_from_path(f"{fileName}.png", config=config, anon=False)['link']
        print("[log:INFO] Done upload.")
    except Exception as e:
        print(f"[log:ERROR] Unable to upload: {e}")
        imgurl = 'https://i.imgur.com/RFmkvQX.jpg'  # 預設錯誤圖片
    
    return imgurl
