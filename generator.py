import feedparser
import requests
from bs4 import BeautifulSoup
import datetime
import PyRSS2Gen

class FeedAggregator:
    def __init__(self):
        self.feeds = []
        
    def add_url(self, url):
        """Try different methods to get RSS feed from a URL"""
        try:
            # First try direct RSS/Atom feed
            feed = feedparser.parse(url)
            if feed.entries:
                self.feeds.append(feed)
                return True
                
            # Try to find RSS link in HTML
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for RSS/Atom links
            feed_links = soup.find_all('link', type=lambda t: t and ('rss' in t or 'atom' in t))
            
            if feed_links:
                feed_url = feed_links[0].get('href')
                if not feed_url.startswith('http'):
                    feed_url = url.rstrip('/') + '/' + feed_url.lstrip('/')
                feed = feedparser.parse(feed_url)
                self.feeds.append(feed)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return False
            
    def generate_combined_feed(self, output_file="combined_feed.xml"):
        """Generate a combined RSS feed from all sources"""
        items = []
        
        for feed in self.feeds:
            for entry in feed.entries:
                pub_date = (entry.get('published_parsed') or 
                           entry.get('updated_parsed') or 
                           datetime.datetime.now().timetuple())
                
                item = PyRSS2Gen.RSSItem(
                    title=entry.get('title', 'No Title'),
                    link=entry.get('link', ''),
                    description=entry.get('summary', ''),
                    pubDate=datetime.datetime.fromtimestamp(
                        datetime.datetime(*pub_date[:6]).timestamp()
                    )
                )
                items.append(item)
        
        # Sort items by publication date
        items.sort(key=lambda x: x.pubDate, reverse=True)
        
        # Create the RSS feed
        rss = PyRSS2Gen.RSS2(
            title="AI and ML News Aggregator",
            link="https://example.com/feed",
            description="Aggregated AI and ML news from multiple sources",
            lastBuildDate=datetime.datetime.now(),
            items=items
        )
        
        # Write to file
        rss.write_xml(open(output_file, "w", encoding='utf-8'))
        return output_file

# Usage example
urls = [
    "https://arxiv.org/list/cs.AI/recent",
    "https://ai.googleblog.com",
    "https://aws.amazon.com/blogs/machine-learning",
    "https://blogs.microsoft.com/ai",
    "https://deepmind.com/blog",
    "https://openai.com/blog",
    "https://www.technologyreview.com/topic/artificial-intelligence/",
    "https://venturebeat.com/category/ai/"
]

def main():
    aggregator = FeedAggregator()
    
    print("Processing URLs...")
    for url in urls:
        success = aggregator.add_url(url)
        print(f"{url}: {'Success' if success else 'Failed'}")
    
    output_file = aggregator.generate_combined_feed()
    print(f"\nCombined feed generated: {output_file}")

if __name__ == "__main__":
    main()
