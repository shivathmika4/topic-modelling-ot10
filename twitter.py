from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

# Global file name
JSON_FILENAME = "tweets_data.json"

def scrape_nitter_hashtag(hashtag, duration=60):
    """Scrapes tweets for a given hashtag and stores them in a JSON file."""
    
    # Setup ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Nitter search URL
    nitter_url = f"https://nitter.net/search?q=%23{hashtag}"
    driver.get(nitter_url)

    start_time = time.time()
    seen_tweets = set()  # Store already collected tweets
    tweets_list = []  # List to store tweets for saving

    try:
        while time.time() - start_time < duration:
            wait = WebDriverWait(driver, 10)
            tweets = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tweet-content media-body']")))

            for tweet in tweets:
                text = tweet.text.strip()
                if text not in seen_tweets:  # Avoid duplicates
                    print(text)
                    print("-" * 50)
                    seen_tweets.add(text)
                    tweets_list.append({"hashtag": hashtag, "tweet": text})  # Store as dictionary

            # Scroll to load more tweets
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(5)  # Allow time to load new tweets

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()

        # Load existing data if the file already exists
        if os.path.exists(JSON_FILENAME):
            with open(JSON_FILENAME, "r", encoding="utf-8") as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append new tweets to existing data
        existing_data.extend(tweets_list)

        # Save updated data back to JSON file
        with open(JSON_FILENAME, "w", encoding="utf-8") as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        print(f"✅ {len(tweets_list)} tweets added to {JSON_FILENAME}")

# Loop to accept multiple hashtags
while True:
    hashtag = input("Enter a hashtag (or type 'exit' to stop): ").strip("#")
    if hashtag.lower() == "exit":
        print("🔹 Exiting... All tweets are stored in tweets_data.json")
        break
    scrape_nitter_hashtag(hashtag)