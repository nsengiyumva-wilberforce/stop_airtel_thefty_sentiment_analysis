from twikit import Client, TooManyRequests
from datetime import datetime, timedelta
from configparser import ConfigParser
from random import randint
import csv
import asyncio
import os
import json

client = Client(language='en-US')

# Queries focused on Uganda mobile money complaints from general public
UGANDA_QUERIES = [
    # General complaints with Uganda context
    '(mobile money OR momo OR airtel money OR mtn momo) (problem OR issue OR complaint) Uganda lang:en',
    '(mobile money failed OR transaction failed) Uganda lang:en',
    '("my money has not been received" OR "transaction failed but money deducted") Uganda lang:en',
    
    # Provider-specific complaints
    '(airtel money complaint OR #StopAirtelTheft) Uganda lang:en',
    '(mtn momo complaint OR mtn mobile money issue) Uganda lang:en',
    
    # General mobile money issues in Uganda
    '("mobile money not working" OR "momo down") Uganda lang:en',
    '("mobile money fraud" OR "mobile money scam") Uganda lang:en',
    
    # Hashtags related to mobile money in Uganda
    '#MobileMoneyFraud Uganda lang:en',
    '#AirtelMoneyComplaint lang:en'
]

# Keywords to identify complaints
COMPLAINT_KEYWORDS = [
    'complaint', 'problem', 'issue', 'failed', 'not working', 'error',
    'fraud', 'scam', 'stolen', 'lost', 'not received', 'deducted',
    'failed transaction', 'refund', 'customer care', 'help', 'support',
    'cheat', 'thief', 'theft', 'stuck', 'pending', 'delay'
]

def is_complaint(tweet_text):
    """Check if tweet text contains complaint-related keywords"""
    text_lower = tweet_text.lower()
    return any(keyword in text_lower for keyword in COMPLAINT_KEYWORDS)

def fix_cookie_file():
    """Fix the cookie file by removing duplicate entries and ensuring proper format"""
    if os.path.exists('cookies.json'):
        try:
            with open('cookies.json', 'r') as f:
                cookies_data = json.load(f)
            
            # Handle different possible cookie formats
            if isinstance(cookies_data, list):
                cookies = cookies_data
            elif isinstance(cookies_data, dict) and 'cookies' in cookies_data:
                cookies = cookies_data['cookies']
            else:
                raise ValueError("Unknown cookie format")
            
            # Remove duplicate cookies (prioritizing the most recent ones)
            unique_cookies = {}
            for cookie in cookies:
                if isinstance(cookie, dict) and 'name' in cookie:
                    # Use (name, domain) as key to identify unique cookies
                    key = (cookie['name'], cookie.get('domain', ''))
                    unique_cookies[key] = cookie
            
            # Save the fixed cookies
            with open('cookies.json', 'w') as f:
                json.dump(list(unique_cookies.values()), f)
            
            print("Fixed cookies.json file")
            return True
        except Exception as e:
            print(f"Error fixing cookie file: {e}")
            # If we can't fix it, remove it
            if os.path.exists('cookies.json'):
                os.remove('cookies.json')
                print("Removed corrupted cookies.json file")
            return False
    return False

async def search_with_query(query, since_date, until_date, product_type='Top'):
    """Search with a specific query and date range"""
    full_query = f"{query} since:{since_date} until:{until_date}"
    print(f'{datetime.now()} - Searching: {full_query} (Product: {product_type})')
    try:
        return await client.search_tweet(full_query, product=product_type, count=100)
    except Exception as e:
        if "Multiple cookies exist with name=ct0" in str(e) or "ct0" in str(e).lower():
            print("Cookie error detected, attempting to fix...")
            if fix_cookie_file():
                try:
                    client.load_cookies('cookies.json')
                    # Retry the search
                    return await client.search_tweet(full_query, product=product_type, count=100)
                except Exception as retry_error:
                    print(f"Retry failed after cookie fix: {retry_error}")
                    return None
            else:
                print("Cookie fix failed, need to reauthenticate")
                return None
        else:
            print(f"Error with query {full_query}: {e}")
            return None

async def get_uganda_mobile_money_complaints(start_date, end_date):
    """Get all Uganda mobile money complaints for a specific date range"""
    all_complaints = []
    collected_tweet_ids = set()  # To avoid duplicates
    
    # Try different product types
    product_types = ['Top', 'Latest']
    
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=7)  # Search one week at a time
        if next_date > end_date:
            next_date = end_date
            
        for query in UGANDA_QUERIES:
            for product_type in product_types:
                tweets = await search_with_query(
                    query, 
                    current_date.strftime('%Y-%m-%d'), 
                    next_date.strftime('%Y-%m-%d'),
                    product_type
                )
                
                if not tweets:
                    continue
                    
                page_count = 1
                has_more_pages = True
                
                while has_more_pages:
                    new_complaints = 0
                    for tweet in tweets:
                        # Check if it's a complaint and not already collected
                        if tweet.id not in collected_tweet_ids and is_complaint(tweet.text):
                            all_complaints.append(tweet)
                            collected_tweet_ids.add(tweet.id)
                            new_complaints += 1
                    
                    print(f"Found {new_complaints} new complaints on page {page_count} (total: {len(all_complaints)})")
                    
                    # Try to get next page
                    try:
                        wait_time = randint(3, 7)  # Respectful delay
                        await asyncio.sleep(wait_time)
                        next_tweets = await tweets.next()
                        
                        if not next_tweets or len(next_tweets) == 0:
                            has_more_pages = False
                        else:
                            tweets = next_tweets
                            page_count += 1
                    except TooManyRequests as e:
                        rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                        print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
                        wait_time = (rate_limit_reset - datetime.now()).total_seconds() + 10
                        await asyncio.sleep(wait_time)
                    except Exception as e:
                        print(f"Error getting next page: {e}")
                        has_more_pages = False
        
        current_date = next_date + timedelta(days=1)  # Move to next day after the range
        
        # Save progress periodically
        if len(all_complaints) > 0 and len(all_complaints) % 100 == 0:
            await save_complaints_to_csv(all_complaints, "uganda_mobile_money_complaints.csv")
            print(f"Saved {len(all_complaints)} complaints to file")
    
    return all_complaints

async def save_complaints_to_csv(complaints, filename):
    """Save complaints to CSV file with additional details"""
    with open(filename, 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            'Tweet_ID', 'Date', 'Username', 'Text', 'Complaint_Type', 'Mobile_Network',
            'Retweets', 'Likes', 'Replies'
        ])
        
        for tweet in complaints:
            # Extract complaint type and mobile network
            complaint_type = categorize_complaint(tweet.text)
            mobile_network = detect_mobile_network(tweet.text)
            
            # Try to get reply count
            reply_count = getattr(tweet, 'reply_count', 'N/A')
                
            tweet_data = [
                tweet.id,
                tweet.created_at,
                tweet.user.name,
                tweet.text,
                complaint_type,
                mobile_network,
                tweet.retweet_count,
                tweet.favorite_count,
                reply_count
            ]
            writer.writerow(tweet_data)

def categorize_complaint(text):
    """Categorize the type of complaint"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['failed transaction', 'transaction failed', 'not completed']):
        return 'Failed Transaction'
    elif any(word in text_lower for word in ['not received', 'money not', 'has not been received']):
        return 'Money Not Received'
    elif any(word in text_lower for word in ['deducted', 'taken', 'stolen', 'fraud']):
        return 'Unauthorized Deduction'
    elif any(word in text_lower for word in ['customer care', 'support', 'help', 'service']):
        return 'Poor Customer Service'
    elif any(word in text_lower for word in ['network', 'not working', 'down', 'error']):
        return 'System/Network Issue'
    elif any(word in text_lower for word in ['charges', 'fees', 'cost', 'expensive']):
        return 'High Charges/Fees'
    else:
        return 'General Complaint'

def detect_mobile_network(text):
    """Detect which mobile network is mentioned in the complaint"""
    text_lower = text.lower()
    
    if 'airtel' in text_lower or 'airtel money' in text_lower:
        return 'Airtel'
    elif 'mtn' in text_lower or 'momo' in text_lower:
        return 'MTN'
    elif 'africell' in text_lower:
        return 'Africell'
    elif 'utl' in text_lower:
        return 'UTL'
    else:
        return 'Unknown'

async def main():
    config = ConfigParser()
    config.read('config.ini')
    
    if not config.has_section('X'):
        print("Error: config.ini missing [X] section")
        return
        
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    # Authentication with better error handling
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if os.path.exists('cookies.json'):
                client.load_cookies('cookies.json')
                # Verify authentication
                user = await client.user()
                print(f"Authenticated as: {user.name} (@{user.screen_name})")
                break
            else:
                await client.login(auth_info_1="####", auth_info_2="####", password="####")
                client.save_cookies('cookies.json')
                print("Successfully logged in and saved cookies")
                break
        except Exception as e:
            print(f"Authentication attempt {attempt+1} failed: {e}")
            if os.path.exists('cookies.json'):
                os.remove('cookies.json')
            if attempt == max_retries - 1:
                print("Max authentication attempts reached. Exiting.")
                return

    # Define date ranges to search
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 8, 31)
    
    print(f"Starting complaint collection from {start_date} to {end_date}")
    
    # Get all complaints for the date range
    all_complaints = await get_uganda_mobile_money_complaints(start_date, end_date)
    
    # Save all complaints to final CSV
    await save_complaints_to_csv(all_complaints, "uganda_mobile_money_complaints.csv")
    
    print(f'{datetime.now()} - Done! Collected {len(all_complaints)} complaints')

if __name__ == "__main__":
    asyncio.run(main())