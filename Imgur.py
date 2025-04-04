# Imgur.py
import matplotlib
matplotlib.use('Agg')
from imgurpython import ImgurClient
import os
import datetime

def showImgur(fileName):
    # 從環境變數獲取 Imgur 憑證
    client_id = os.getenv('a96e89125fec0f2')
    client_secret = os.getenv('57e2995622d333a54c58f835421a09283346706d')
    album_id = os.getenv('ebff4c74408a2c944bbb450ef28d2340f990d2b4')
    access_token = os.getenv('7c1328f8fd123327b955fb8d189e5fb62c4ba24d')
    refresh_token = os.getenv('stock')

    # 檢查憑證是否有效
    if not all([client_id, client_secret, access_token, refresh_token]):
        missing = [k for k, v in {'client_id': client_id, 'client_secret': client_secret, 
                                 'access_token': access_token, 'refresh_token': refresh_token}.items() if not v]
        print(f"[log:ERROR] Missing Imgur credentials: {missing}")
        return "Imgur 憑證缺失或無效，請聯繫管理員！"

    # 連接到 Imgur
    try:
        client = ImgurClient(client_id, client_secret, access_token, refresh_token)
        
        # 配置參數
        config = {
            'album': album_id if album_id else None,  # 若無 album_id 則設為 None
            'name': fileName,
            'title': fileName,
            'description': str(datetime.date.today())
        }
        
        # 上傳檔案
        print(f"[log:INFO] Uploading image: {fileName}.png")
        imgurl = client.upload_from_path(f"{fileName}.png", config=config, anon=False)['link']
        print(f"[log:INFO] Done upload. URL: {imgurl}")
    except Exception as e:
        print(f"[log:ERROR] Unable to upload: {e}")
        imgurl = "圖片上傳失敗，請稍後再試！"
    
    return imgurl
