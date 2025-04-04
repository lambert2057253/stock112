'''
Upload pics
'''
import matplotlib
matplotlib.use('Agg')
from imgurpython import ImgurClient
import os
import datetime

def showImgur(fileName):
    client_id = os.getenv('IMGUR_CLIENT_ID')
    client_secret = os.getenv('IMGUR_CLIENT_SECRET')
    album_id = os.getenv('IMGUR_ALBUM_ID')
    access_token = os.getenv('IMGUR_ACCESS_TOKEN')
    refresh_token = os.getenv('IMGUR_REFRESH_TOKEN')

    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    
    config = {
        'album': album_id,
        'name': fileName,
        'title': fileName,
        'description': str(datetime.date.today())
    }
    
    try:
        print(f"[log:INFO] Uploading image: {fileName}.png")
        imgurl = client.upload_from_path(f"{fileName}.png", config=config, anon=False)['link']
        print("[log:INFO] Done upload.")
    except Exception as e:
        print(f"[log:ERROR] Unable to upload: {e}")
        imgurl = "圖片上傳失敗，請檢查 Imgur 憑證或檔案！"
    
    return imgurl
