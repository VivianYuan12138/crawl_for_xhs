import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

df_columns = ['Note ID', 'Note Title', 'User ID', 'Username', 'Profile Picture URL',
              'Note Publish Time', 'IP Location', 'Note Comment Count',
              'Note Like Count', 'Note Collection Count', 'Keywords', 'Note Content']

def save_to_csv(data, csv_file_path, mode='w'):
    df = pd.DataFrame(data, columns=df_columns)
    df.to_csv(csv_file_path, mode=mode, index=False, encoding='utf_8_sig', header=(mode == 'w'))


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

        comment_count = get_meta_content('og:xhs:note_comment')
        like_count = get_meta_content('og:xhs:note_like')
        collect_count = get_meta_content('og:xhs:note_collect')
        keywords = get_meta_content('keywords')
        description = get_meta_content('description')

        return date, location, comment_count, like_count, collect_count, keywords, description

    except Exception as e:
        print(f"Error fetching data from {sub_link}: {e}")
        return [None] * 7

def scrape_xiaohongshu(base_url, headers, params, csv_file_path):
    note_data = []
    page = 0
    while True:
        time.sleep(1)  # Delay between requests
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print("Failed to fetch data with status code:", response.status_code)
            break

        data = response.json()
        page += 1

        has_more = data['data']['has_more']
        if not has_more:
            print('No more pages, stopping the loop!')
            break

        for note in data['data']['notes']:
            note_id = note['id']
            title = note.get('title', 'No Title')
            user_id = note['user']['userid']
            username = note['user']['nickname']
            profile_pic_url = note['user']['images']
            sub_link = f'https://www.xiaohongshu.com/explore/{note_id}'
            sub_data = fetch_sub_link_data(sub_link)

            note_data.append([note_id, title, user_id, username, profile_pic_url] + list(sub_data))
        
        # Save to CSV every 10 pages
        if page % 10 == 0:
            print(f'Scraped {page} pages')
            save_to_csv(note_data, csv_file_path, mode='a' if page > 10 else 'w')
            note_data = []

        params['cursor'] = data['data']['cursor']
    
    # Save remaining data to CSV
    if note_data:
        save_to_csv(note_data, csv_file_path, mode='a' if page > 10 else 'w')


    return note_data, page



# Initialization
base_url = "https://www.xiaohongshu.com/web_api/sns/v3/page/notes"
headers = {'User-Agent': 'Mozilla/5.0 ...'}
params = {
    'page_size': 6,
    'sort': 'hot',
    'page_id': '6102992b0ce64500013fc9e4',
    'cursor': ''
}
csv_file_path = 'xiaohongshu_data.csv'

# Record start time
start_time = time.time()

# Scraping
pages_scraped = scrape_xiaohongshu(base_url, headers, params, csv_file_path)

# Record end time
end_time = time.time()

print(f'Time elapsed: {end_time - start_time:.2f} seconds')
print(f'Finished scraping {pages_scraped} pages!')