import requests
from bs4 import BeautifulSoup
import time
from settings import *

proxyDict = {'http': http_proxy,
             'https': https_proxy}

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
}

def make_item_str(blocks):
    item_list = []
    for item_block in blocks[10::-1]:
        name = item_block.find('span', {'itemprop': 'name'}).text
        price = item_block.find('span', {'itemprop': 'price'}).text
        url_item = item_block.find('a', {'class': 'item-description-title-link', 'itemprop': 'url'}).get('href')
        item_info = name + price + '\n' + 'http://avito.ru/' + url_item
        item_list.append(item_info)
    return item_list


def send_telegram(text):
    token = telegram_token
    url_api = "https://api.telegram.org/bot"
    url_api += token
    method = url_api + "/sendMessage"

    for channel_id in channel_ids:
        r = requests.post(method, data={"chat_id": channel_id, "text": text}, proxies=proxyDict)

        if r.status_code != 200:
            print(f'Не удалось отправить сообщение в Telegramm: {text} в {time.ctime(time.time())}')

def search_update():
    old_items_list = []
    while True:
        while True:
            try:
                response = requests.get(url, proxies=proxyDict, headers=headers)
            except Exception as error:
                print(error)
                print(time.ctime(time.time()))
                time.sleep(5)
            else:
                page = response.content.decode('utf-8')
                soup = BeautifulSoup(page)
                items_blocks = soup.find_all('div', {'class': 'item-with-contact', 'data-type': '1'})
                items_list = make_item_str(items_blocks)
                if items_list:
                    break

        if old_items_list:
            items_list_set = set(items_list)
            old_items_list_set = set(old_items_list)

            if items_list_set != old_items_list_set:
                new_items = items_list_set.difference(old_items_list_set)
                for item in new_items:
                    send_telegram(item)
        else:
            old_items_list = items_list

        time.sleep(update_time)

search_update()