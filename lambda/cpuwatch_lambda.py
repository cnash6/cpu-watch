#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import time
import json
import boto3
import os

s3 = boto3.client('s3')
s3bucket = os.environ['s3bucket']
filename = os.environ['filename']

def lambda_handler(event, context):

    items = json.loads(s3.get_object(Bucket=s3bucket, Key=filename)['Body'].read().decode('utf-8'))
    
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
            message = f'Inventory Updates:\n\n{chr(10).join(changed)}'
            print(message)
            boto3.client('sns').publish(
                PhoneNumber=items['number'],
                Message=message
            )
            s3.put_object(Bucket='cpuwatch', Key='items.json', Body=json.dumps(items))
    except:
        print(f'Encountered exception fetching prices at {upT}')

if __name__ == "__main__":
    lambda_handler(None, None)