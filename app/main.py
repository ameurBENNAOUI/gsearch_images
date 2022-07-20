import os
from timeit import default_timer as timer
import requests, lxml, re, json, urllib.request
from bs4 import BeautifulSoup
import uvicorn
from fastapi import FastAPI
from starlette.status import HTTP_403_FORBIDDEN
import os
from fastapi.responses import JSONResponse
from timeit import default_timer as timer
import requests, lxml, re, json, urllib.request
from bs4 import BeautifulSoup
import uvicorn

headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
}


def get_original_images(soup):
    original_images=[]  
    print('\nGoogle Images Metadata:')
    for google_image in soup.select('.isv-r.PNCib.MSM1fd.BUooTd'):
        title = google_image.select_one('.VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb')['title']
        source = google_image.select_one('.fxgdke').text
        link = google_image.select_one('.VFACy.kGQAp.sMi44c.lNHeqe.WGvvNb')['href']
        
        print(f'{title}\n{source}\n{link}\n')

    all_script_tags = soup.select('script')

    matched_images_data = ''.join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(all_script_tags)))
    
   
    matched_images_data_fix = json.dumps(matched_images_data)
    matched_images_data_json = json.loads(matched_images_data_fix)

    matched_google_image_data = re.findall(r'\[\"GRID_STATE0\",null,\[\[1,\[0,\".*?\",(.*),\"All\",', matched_images_data_json)

    matched_google_images_thumbnails = ', '.join(
        re.findall(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]',
                   str(matched_google_image_data))).split(', ')

    print('Google Image Thumbnails:')  # in order
    for fixed_google_image_thumbnail in matched_google_images_thumbnails:
        google_image_thumbnail_not_fixed = bytes(fixed_google_image_thumbnail, 'ascii').decode('unicode-escape')

        google_image_thumbnail = bytes(google_image_thumbnail_not_fixed, 'ascii').decode('unicode-escape')
        print(google_image_thumbnail)

    removed_matched_google_images_thumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', '', str(matched_google_image_data))


    matched_google_full_resolution_images = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
                                                       removed_matched_google_images_thumbnails)


    print('\nFull Resolution Images:')  # in order
    for index, fixed_full_res_image in enumerate(matched_google_full_resolution_images):
        
        original_size_img_not_fixed = bytes(fixed_full_res_image, 'ascii').decode('unicode-escape')
        original_size_img = bytes(original_size_img_not_fixed, 'ascii').decode('unicode-escape')
        original_images.append(original_size_img)
        print(original_size_img)

   
    return  original_images  

app = FastAPI(openapi_url="/openapi.json", docs_url="/docs",title='Gsearch Engine  API')


@app.get("/gsearch",tags=["google search"])
async def search(keywords:str):
    # &source=lnms&tbs=isz:lt,islt:2mp&safe,=active
    params = {
        "q": keywords, 
        "safe"="active",
        "tbm": "isch",                # image results
        "hl": "en",                   # language
        "ijn": "0"     }
    html = requests.get("https://www.google.com/search", params=params, headers=headers, timeout=30)
    soup = BeautifulSoup(html.text, 'lxml')  
    data= get_original_images(soup)
    print("======================================================")
    print(len(data))
    return JSONResponse(content=data)
#if __name__ == "__main__":
#   uvicorn.run("main:app", host="0.0.0.0", port=8000)