import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from datetime import datetime
import json
import os

# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")
from nltk.corpus import stopwords


class NewsTracker:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        # Add common words that appear on news sites that we want to ignore
        self.stop_words.update(["said", "would", "could", "also"])

        # Create data directory if it doesn't exist
        if not os.path.exists("data"):
            os.makedirs("data")

    def fetch_article(self, url):
        """Fetch article content from URL"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text(self, html):
        """Extract readable text from HTML"""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.decompose()

        # Find main article content (customize these selectors based on the website)
        article_selectors = ["article", ".article-content", ".story-content"]
        for selector in article_selectors:
            content = soup.select(selector)
            if content:
                return " ".join(p.get_text() for p in content)

        # Fallback to main content
        return soup.get_text()

    def process_text(self, text):
        """Process text and count word frequencies"""
        if not text:
            return Counter()

        # Tokenize words
        words = nltk.word_tokenize(text.lower())

        # Filter words
        words = [
            word
            for word in words
            if (
                word.isalnum()  # only alphanumeric
                and len(word) > 3  # longer than 3 characters
                and word not in self.stop_words  # not a stop word
            )
        ]

        return Counter(words)

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
            json.dump(word_counts, f, indent=2)

    def display_top_words(self, word_counts, limit=50):
        """Display the most frequent words"""
        print("\nTop words:")
        print("-" * 30)
        for word, count in word_counts.most_common(limit):
            print(f"{word}: {count}")


def main():
    # Initialize tracker
    tracker = NewsTracker()

    # Example URLs (replace with actual news URLs)
    urls = [
        "https://www.nytimes.com/",  # Replace with real URLs
        "https://www.wsj.com/",
        "https://news.ycombinator.com/",
        "https://www.cnn.com/",
        "https://www.bbc.com/",
        "https://www.reuters.com/",
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

        # Fetch and process content
        html = tracker.fetch_article(url)
        if html:
            text = tracker.extract_text(html)
            word_counts = tracker.process_text(text)
            all_words.update(word_counts)

    # Save and display results
    tracker.save_results(all_words, "example_source")
    tracker.display_top_words(all_words)


if __name__ == "__main__":
    main()
