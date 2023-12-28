import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os

# 代理配置，设置为你的本地代理服务器地址和端口
proxy_url = 'http://your_proxy_server_address:your_proxy_server_port'
proxy = {
    'http': proxy_url,
    'https': proxy_url
}

df_columns = ['nickname', 'link', 'title', 'date', 'location', 'like_count', 'collect_count', 'comment_count', 'keywords', 'description']

# 获取个人主页的所有note的url
def get_note_url_list(urls):
    for url in urls:
        try:
            response = requests.get(f'http://www.xiaohongshu.com/user/profile/{url}', proxies=proxy)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            nickname = soup.find('div', class_='user-name').text.strip()

            # 模拟滚动以加载更多内容
            scroll_times = 15
            visited_urls = set()

            for _ in range(scroll_times):
                # 将页面滚动一段距离
                js = "window.scrollBy(0, 500);"
                driver.execute_script(js)
                time.sleep(1)  # 等待页面加载新内容

                soup = BeautifulSoup(response.text, 'html.parser')
                note_url_elements = soup.select('section.note-item a[href*="/explore/"]')

                for url_element in note_url_elements:
                    note_url = 'https://www.xiaohongshu.com' + url_element['href']
                    if note_url not in visited_urls:
                        visited_urls.add(note_url)
                        print(note_url)
                        data = fetch_sub_link_data(note_url)
                        write_data_to_csv(nickname, note_url, data)

            print(f"Found {len(visited_urls)} notes for {nickname}")
        except Exception as e:
            print(f"Error fetching data for {url}: {e}")

def write_data_to_csv(nickname, note_url, data):
    combined_data = [nickname, note_url] + list(data)
    df = pd.DataFrame([combined_data], columns=df_columns)
    df.to_csv(f'{nickname}.csv', mode='a', index=False, header=not os.path.exists(f'{nickname}.csv'), encoding='utf-8-sig')

def fetch_sub_link_data(sub_link):
    try:
        response = requests.get(sub_link, proxies=proxy)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        date_location_info = soup.find('span', class_='date').text.strip()
        bottom_container = soup.find('div', class_='bottom-container')

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

        return title, date, location, like_count, collect_count, comment_count, keywords, description

    except Exception as e:
        print(f"Error fetching data from {sub_link}: {e}")
        return [None] * 8

# m站个人主页的地址
get_note_url_list([
    '5597c64f3397db57ef473fac',
    # 添加更多用户的URL
])

# 如何查看本地代理设置：
# 1. 在浏览器中打开代理设置页面。这个页面的位置和方式会根据你使用的操作系统和浏览器而有所不同。
# 2. 在Windows中，你可以打开“Internet选项”，然后在“连接”选项卡下找到“局域网设置”按钮。
# 3. 在macOS中，你可以在“系统偏好设置”中找到“网络”，然后点击左下角的“高级”按钮，接着在“代理”选项卡下查看设置。
# 4. 在Linux中，你可以根据你使用的桌面环境和网络管理工具来查看代理设置。
# 5. 在代理设置页面，你可以查看和配置代理服务器的地址和端口，也可以启用或禁用代理。
