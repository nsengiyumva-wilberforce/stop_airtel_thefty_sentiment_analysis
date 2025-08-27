import asyncio
from twikit import Client, TooManyRequests
from datetime import datetime
import csv
import configparser

USERNAME = '#####'
EMAIL = '#####'
PASSWORD = '###'

# Initialize client
client = Client('en-US')

async def main():
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file='cookies.json'
    )
    tweets = await client.get_user_tweets('123456', 'Tweets')

    for tweet in tweets:
        print(tweet.text)

asyncio.run(main())