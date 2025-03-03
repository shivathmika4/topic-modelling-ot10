from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_nitter_hashtag(hashtag, duration=60):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    nitter_url = f"https://nitter.net/search?q=%23{hashtag}"
    driver.get(nitter_url)

    start_time = time.time()
    seen_tweets = set()  # Store already printed tweets

    try:
        while time.time() - start_time < duration:
            wait = WebDriverWait(driver, 10)
            tweets = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='tweet-content media-body']")))

            for tweet in tweets:
                text = tweet.text.strip()
                if text not in seen_tweets:  # Avoid duplicate tweets
                    print(text)
                    print("-" * 50)
                    seen_tweets.add(text)

            # Scroll to load more tweets
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(5)  # Allow time to load new tweets

    except Exception as e:
        print("Error:", e)

    finally:
        driver.quit()

# Example usage
hashtag = input("Enter a hashtag: ").strip("#")
scrape_nitter_hashtag(hashtag)
