import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from datetime import datetime
import json
import os
import time  # Added for rate limiting

nltk.download("punkt")
nltk.download("stopwords")
from nltk.corpus import stopwords


class NewsTracker:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        # Expanded list of common news-related words to ignore
        self.stop_words.update(
            [
                "said",
                "would",
                "could",
                "also",
                "says",
                "according",
                "reported",
                "told",
                "year",
                "years",
                "time",
                "people",
                "like",
                "just",
                "make",
                "made",
                "new",
                "first",
                "last",
                "week",
                "day",
                "days",
                "weeks",
                "month",
                "months",
                "hours",
            ]
        )

        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

    def fetch_article(self, url):
        """Fetch article content from URL with better error handling"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Successfully fetched {url} (Status: {response.status_code})")
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def extract_text(self, html):
        """Extract readable text from HTML with improved selectors"""
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for element in soup(
            ["script", "style", "nav", "header", "footer", "aside", "noscript"]
        ):
            element.decompose()

        # Expanded list of content selectors for different news sites
        article_selectors = [
            "article",
            ".article-content",
            ".story-content",
            ".story-body",
            ".main-content",
            "#main-content",
            ".article__content",
            ".article-body",
            ".content-article",
            "[role='main']",
            ".story",
            ".post-content",
        ]

        # Try to find content using selectors
        for selector in article_selectors:
            content = soup.select(selector)
            if content:
                return " ".join(p.get_text() for p in content)

        # Fallback to main content
        return soup.get_text()

    def process_text(self, text):
        """Process text and count word frequencies with improved filtering"""
        if not text:
            return Counter()

        try:
            # Tokenize words
            words = nltk.word_tokenize(text.lower())

            # Enhanced filtering
            words = [
                word
                for word in words
                if (
                    word.isalnum()
                    and len(word) > 3
                    and word not in self.stop_words
                    and not word.isnumeric()  # Remove pure numbers
                )
            ]

            return Counter(words)
        except Exception as e:
            print(f"Error processing text: {e}")
            return Counter()

    def save_results(self, word_counts, source):
        """Save word frequencies to a JSON file with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data/{source}_{timestamp}.json"

        # Convert Counter to dictionary and sort by count
        sorted_counts = dict(
            sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        )

        # Save updated data
        with open(filename, "w") as f:
            json.dump(sorted_counts, f, indent=2)
        print(f"\nSaved results to {filename}")

    def display_top_words(self, word_counts, limit=50):
        """Display the most frequent words with count visualization"""
        print("\nTop words:")
        print("-" * 50)

        # Find maximum count for scaling
        max_count = max(count for count in word_counts.values()) if word_counts else 0

        for word, count in word_counts.most_common(limit):
            # Create a simple bar visualization
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length
            print(f"{word:20} {count:5d} {bar}")


def main():
    # Initialize tracker
    tracker = NewsTracker()

    # Start with a smaller set of more reliable news sites
    urls = [
        "https://www.nytimes.com/",  # Replace with real URLs
        "https://www.wsj.com/",
        "https://news.ycombinator.com/",
        "https://www.cnn.com/",
        "https://www.bbc.com/",
        # "https://www.reuters.com/",
        "https://www.theguardian.com/",
        "https://www.aljazeera.com/",
        "https://www.npr.org/",
        "https://www.bloomberg.com/",
        "https://www.economist.com/",
        "https://www.ft.com/",
        "https://www.nbcnews.com/",
        "https://www.usatoday.com/",
        "https://www.latimes.com/",
        "https://www.chicagotribune.com/",
        # "https://www.washingtonpost.com/",
        "https://www.foxnews.com/",
        "https://www.huffpost.com/",
        "https://www.politico.com/",
        "https://www.apnews.com/",
        "https://www.axios.com/",
        "https://www.buzzfeednews.com/",
        "https://www.vice.com/",
        "https://www.msnbc.com/",
        "https://www.bbc.co.uk/news",
        "https://www.thetimes.co.uk/",
        "https://www.telegraph.co.uk/",
        "https://www.independent.co.uk/",
        "https://www.mirror.co.uk/",
        "https://www.express.co.uk/",
        "https://www.dailymail.co.uk/",
        "https://www.thesun.co.uk/",
    ]

    # Process each URL
    all_words = Counter()
    for url in urls:
        print(f"\nProcessing: {url}")
        html = tracker.fetch_article(url)
        if html:
            text = tracker.extract_text(html)
            word_counts = tracker.process_text(text)
            all_words.update(word_counts)
            # time.sleep(2)  # Be polite with requests

    # Save and display results
    if all_words:
        tracker.save_results(all_words, "news_tracker")
        tracker.display_top_words(all_words)
    else:
        print("No words were processed. Check if the websites were properly accessed.")


if __name__ == "__main__":
    main()
