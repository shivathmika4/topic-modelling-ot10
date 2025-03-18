from flask import Flask, render_template, request, redirect, url_for
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

# Initialize Flask app
app = Flask(__name__)

# File to store scraped tweets
TWEETS_FILE = "tweets_data.json"

# Function to scrape tweets from Nitter
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
            time.sleep(1)  # Allow time to load new tweets

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()

        # Load existing data if the file already exists
        if os.path.exists(TWEETS_FILE):
            with open(TWEETS_FILE, "r", encoding="utf-8") as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append new tweets to existing data
        existing_data.extend(tweets_list)

        # Save updated data back to JSON file
        with open(TWEETS_FILE, "w", encoding="utf-8") as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        print(f"✅ {len(tweets_list)} tweets added to {TWEETS_FILE}")
        return tweets_list

# Home route (hashtag input page)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        hashtag = request.form.get("hashtag")
        if not hashtag:
            return render_template("index.html", error="Hashtag is required")

        # Scrape tweets for the given hashtag
        tweets = scrape_nitter_hashtag(hashtag)
        return redirect(url_for("results", hashtag=hashtag))

    return render_template("index.html")

# Results route (display scraped tweets)
@app.route("/results")
def results():
    hashtag = request.args.get("hashtag")
    if not hashtag:
        return redirect(url_for("index"))

    # Load scraped tweets from JSON file
    if os.path.exists(TWEETS_FILE):
        with open(TWEETS_FILE, "r", encoding="utf-8") as json_file:
            try:
                tweets_data = json.load(json_file)
            except json.JSONDecodeError:
                tweets_data = []
    else:
        tweets_data = []

    # Filter tweets for the given hashtag
    tweets = [tweet for tweet in tweets_data if tweet["hashtag"] == hashtag]
    return render_template("results.html", hashtag=hashtag, tweets=tweets)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)