#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import schedule
import time
import json
import boto3

def get_stock():
    items = json.loads(open('items.json', 'r').read())
    changed = []
    upT = time.strftime("%m/%d %H:%M:%S", time.localtime())
    try:
        for i, item in enumerate(items['items']):
            stock = BeautifulSoup(requests.get(item['url']).text, 'html.parser').find_all("span", class_=item['tag'])[0].string
            if stock != item['stock']:
                changed.append(f'{item["item"]} updated from:\n\t{items["items"][i]["stock"]} => {stock}\n\t@ {upT}')
                items['items'][i]['stock'] = stock
                items['items'][i]['updated'] = upT
        print(f'checked at {upT}')
        if changed:
            with open('items.json', 'w') as f:
                f.write(json.dumps(items))

            message = f'Inventory Updates:\n\n{chr(10).join(changed)}'
            print(message)
            boto3.client('sns').publish(
                PhoneNumber=items['number'],
                Message=message
            )
    except:
        print(f'Encountered exception fetching prices at {upT}')

schedule.every(10).minutes.at(":00").do(get_stock)

while True:
    schedule.run_pending()
    time.sleep(1)