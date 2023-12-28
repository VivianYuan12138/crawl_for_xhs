# coding=UTF-8
from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
import time
import requests
import pandas as pd
import os
df_columns = ['nickname', 'link', 'title', 'date', 'location', 'like_count', 'collect_count', 'comment_count', 'keywords', 'description']

# 获取个人主页的所有note的url
def get_note_url_list(urls):
    driver = webdriver.Edge()  # Specify the path to the Edge WebDriver

    for url in urls:
        driver.get('http://www.xiaohongshu.com/user/profile/' + url)
        
        # 获取条目数量
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        nickname = soup.find('div', class_='user-name').text.strip()

        # I cannot get the number of notes from the HTML structure
        # you can try to search for it and set it manually
        scroll_times = 15
        
        # 用于记录已经获取的note_url的集合
        visited_urls = set()
        
        # 模拟滚动以加载更多内容
        for _ in range(scroll_times):
            # 将页面滚动一段距离
            js = "window.scrollBy(0, 500);"
            driver.execute_script(js)
            time.sleep(1)  # 等待页面加载新内容
            
            # 解析链接
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract note URLs from the updated HTML structure with class="note-item"
            note_url_elements = soup.select('section.note-item a[href*="/explore/"]')
            
            for url_element in note_url_elements:
                note_url = 'https://www.xiaohongshu.com' + url_element['href']
                if note_url not in visited_urls:
                    visited_urls.add(note_url)
                    print(note_url)
                    data = fetch_sub_link_data(note_url)
                    write_data_to_csv(nickname, note_url, data)

        print(f"Found {len(visited_urls)} notes for {nickname}")
    driver.close()

def write_data_to_csv(nickname, note_url, data):
    combined_data = [nickname, note_url] + list(data)
    df = pd.DataFrame([combined_data], columns=df_columns)
    df.to_csv(f'{nickname}.csv', mode='a', index=False, header=not os.path.exists(f'{nickname}.csv'), encoding='utf-8-sig')

def fetch_sub_link_data(sub_link):
    try:
        response = requests.get(sub_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        date_location_info = soup.find('span', class_='date').text.strip()
        # First, find the 'bottom-container' div
        bottom_container = soup.find('div', class_='bottom-container')
        # Now, find the 'date' span within the 'bottom-container'
        if bottom_container:
            date_span = bottom_container.find('span', class_='date')
            if date_span:
                date_location_info = date_span.text.strip()
                parts = date_location_info.split(' ')
                date = parts[0]
                location = parts[1] if len(parts) > 1 else None
            else:
                date = None
                location = None
        else:
            date = None
            location = None

        def get_meta_content(name):
            meta = soup.find('meta', attrs={'name': name})
            return meta['content'] if meta else None

        title = get_meta_content('og:title')
        comment_count = get_meta_content('og:xhs:note_comment')
        like_count = get_meta_content('og:xhs:note_like')
        collect_count = get_meta_content('og:xhs:note_collect')
        keywords = get_meta_content('keywords')
        description = get_meta_content('description')

        # return data csv file
        return title, date, location, like_count, collect_count, comment_count, keywords, description

    except Exception as e:
        print(f"Error fetching data from {sub_link}: {e}")
        return [None] * 8




# m站个人主页的地址
get_note_url_list([
    '5597c64f3397db57ef473fac',
    #'62eb8d1f000000001e01fc43',
    # '5d232e6d0000000010009ffd',
    # '5cfcb8de000000001701e066'
    # '5e99ef3b0000000001000970',
    # '554d98baa46e9626b84ebe39',
    # '57367ccf50c4b4528a90f723',
    # '54b0f079b4c4d65f85e76bdc',
    # '5756621a82ec39663c40c45d',
    # '59a65a295e87e75966563793',
    # '561f967641a2b3550b12fd4c',
    # '54f697fb4fac6379b6f3bc95',
    # '596c805750c4b4218d929a59',
])
