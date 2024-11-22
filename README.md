# News Tracker

A Python-based tool for tracking and analyzing word frequencies across major news websites. Available in two versions: a traditional web scraper and a Selenium-based dynamic content scraper.

## Features

- Scrapes text content from multiple news websites
- Analyzes word frequencies across articles
- Filters out common stop words and news-specific terms
- Saves results in JSON format with timestamps

## Installation

1. Clone the repository:
2. Install dependencies:

```
pip install -r requirements.txt
```

## Implementation Details

### Basic News Tracker (`news_tracker.py`)

- Uses BeautifulSoup4 for HTML parsing
- Visual representation of word frequencies
- Processes 40+ major news websites

### Selenium Tracker (`selenium_tracker.py`)

- Handles JavaScript-rendered content
- Dynamic scrolling for infinite-scroll pages
- Chrome headless browser integration

## Sample Output

```
Processing: https://www.example.com
Top words:

---

ukraine 125 ████████████████████
economy 87 █████████████
climate 76 ███████████
...
```
