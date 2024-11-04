import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from nltk.corpus import stopwords
from datetime import datetime
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def setup_nltk():
    """Download required NLTK data packages"""
    required_packages = [
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "stopwords",
    ]
    for package in required_packages:
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            print(f"Error downloading {package}: {e}")


# Initialize NLTK before anything else
setup_nltk()


class NewsTracker:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        # Add common words that appear on news sites that we want to ignore
        # self.stop_words.update(["said", "would", "could", "also"])

        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-extensions")
        self.driver = None

    def setup_driver(self):
        """Initialize the Chrome driver"""
        if not self.driver:
            self.driver = webdriver.Chrome(options=self.chrome_options)
        return self.driver

    def cleanup_driver(self):
        """Clean up the Chrome driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def extract_text_selenium(self, url, scroll_pause_time=1.5, wait_time=10):
        """Extract text using Selenium with dynamic scrolling"""
        try:
            driver = self.setup_driver()
            driver.get(url)

            # Wait for the page to load
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Get initial page height
            last_height = driver.execute_script("return document.body.scrollHeight")

            all_text_chunks = set()

            while True:
                # Extract visible text
                visible_text = driver.execute_script(
                    """
                    function isVisible(elem) {
                        if (!(elem instanceof Element)) return false;
                        const style = getComputedStyle(elem);
                        if (style.display === 'none') return false;
                        if (style.visibility !== 'visible') return false;
                        if (style.opacity < 0.1) return false;
                        const rect = elem.getBoundingClientRect();
                        return !(rect.width === 0 || rect.height === 0);
                    }
                    
                    function getVisibleText(element) {
                        if (!isVisible(element)) return [];
                        return Array.from(element.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,article'))
                            .filter(el => isVisible(el))
                            .map(el => el.textContent.trim())
                            .filter(text => text.length > 0);
                    }
                    
                    return getVisibleText(document.body);
                """
                )

                # Add new text chunks
                for text in visible_text:
                    cleaned_text = re.sub(r"\s+", " ", text).strip()
                    if cleaned_text:
                        all_text_chunks.add(cleaned_text)

                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break

                last_height = new_height

            return " ".join(all_text_chunks)

        except Exception as e:
            print(f"Error extracting text with Selenium: {e}")
            return ""

    def fetch_and_extract(self, url):
        """Fetch and extract text from URL using Selenium"""
        try:
            return self.extract_text_selenium(url)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return ""

    def fetch_article(self, url):
        """Fetch article content from URL"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text(self, html):
        """Extract readable text from HTML while maintaining structure"""
        if not html:
            return ""

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Remove unwanted elements
            for element in soup(["script", "style", "header", "footer", "nav"]):
                element.decompose()

            text_content = []

            # Extract title
            if soup.title:
                text_content.append(f"Title: {soup.title.string.strip()}\n")

            # Process main content with structure
            for element in soup.find_all(
                ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]
            ):
                text = element.get_text().strip()
                if text:
                    if element.name.startswith("h"):
                        text_content.append(f"\n{text}\n")
                    else:
                        text_content.append(text)

            # Join and clean text
            full_text = "\n".join(text_content)
            clean_text = re.sub(r"\n\s*\n", "\n\n", full_text)
            return clean_text.strip()

        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def process_text(self, text):
        """Process text and count word frequencies"""
        if not text:
            return Counter()

        try:
            # Basic word tokenization (more robust than nltk tokenize)
            words = text.lower().split()

            # Filter words
            words = [word.strip('.,!?()[]{}":;') for word in words]
            words = [
                word
                for word in words
                if (
                    word.isalnum()  # only alphanumeric
                    and word not in self.stop_words  # not a stop word
                )
            ]

            return Counter(words)
        except Exception as e:
            print(f"Error processing text: {e}")
            return Counter()

    def save_results(self, word_counts, source):
        """Save word frequencies to a JSON file"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"data/{source}_{date_str}.json"

        # Load existing data if any
        if os.path.exists(filename):
            with open(filename, "r") as f:
                existing_data = json.load(f)
            # Combine with new counts
            for word, count in word_counts.items():
                existing_data[word] = existing_data.get(word, 0) + count
            word_counts = existing_data

        # Save updated data
        with open(filename, "w") as f:
            json.dump(dict(word_counts), f, indent=2)

    def display_top_words(self, word_counts, limit=10):
        """Display the most frequent words"""
        print("\nTop words:")
        print("-" * 30)
        for word, count in word_counts.most_common(limit):
            print(f"{word}: {count}")


def main():
    # Initialize tracker
    tracker = NewsTracker()

    # Let's start with a simpler news site
    urls = [
        "https://www.nytimes.com/",  # Replace with real URLs
        "https://www.wsj.com/",
        "https://www.reuters.com/",
        "https://news.ycombinator.com/",
        "https://www.cnn.com/",
        "https://www.bbc.com/",
    ]

    try:
        all_words = Counter()
        for url in urls:
            print(f"\nProcessing: {url}")
            text = tracker.fetch_and_extract(url)
            if text:
                word_counts = tracker.process_text(text)
                all_words.update(word_counts)

        if all_words:
            tracker.save_results(all_words, "news")
            tracker.display_top_words(all_words)
        else:
            print(
                "No words were processed. Check if the website content was properly accessed."
            )

    finally:
        tracker.cleanup_driver()


if __name__ == "__main__":
    main()
