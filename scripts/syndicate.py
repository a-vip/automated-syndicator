import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# Configuration
DEV_TO_API_URL = "https://dev.to/api/articles"
RSS_FEED_URL = "https://aviperera.com/feed/"
STATE_FILE = "posted.json"

# Secrets
DEV_API_KEY = os.environ.get("DEV_API_KEY")

def load_posted():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted(posted_guids):
    with open(STATE_FILE, "w") as f:
        json.dump(posted_guids, f, indent=2)

def fetch_rss():
    req = urllib.request.Request(RSS_FEED_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"Failed to fetch RSS: {e}")
        return None

def parse_rss(xml_data):
    root = ET.fromstring(xml_data)
    articles = []
    for item in root.findall('./channel/item'):
        guid = item.find('guid').text
        title = item.find('title').text
        link = item.find('link').text
        
        # In WordPress feeds, content is usually in content:encoded, but we'll try description if not found
        content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
        if content_elem is not None:
            content = content_elem.text
        else:
            content = item.find('description').text
            
        articles.append({
            'guid': guid,
            'title': title,
            'link': link,
            'content': content
        })
    # Return oldest first so we post chronologically if there are multiple new ones
    return list(reversed(articles))

def post_to_dev_to(article):
    if not DEV_API_KEY:
        print("Error: DEV_API_KEY environment variable not set.")
        return False
        
    payload = {
        "article": {
            "title": article['title'],
            "body_markdown": f"{article['content']}\n\n*Originally published at [{article['title']}]({article['link']})*",
            "published": True,
            "canonical_url": article['link'],
            "tags": ["ai", "governance", "research", "tech"]
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(DEV_TO_API_URL, data=data, headers={
        'Content-Type': 'application/json',
        'api-key': DEV_API_KEY,
        'User-Agent': 'Mozilla/5.0'
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print(f"Successfully posted to Dev.to: {res.get('url')}")
            return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8')
        print(f"Failed to post to Dev.to. Status: {e.code}. Error: {err_msg}")
        return False
    except Exception as e:
        print(f"Exception while posting to Dev.to: {e}")
        return False

def main():
    print("Starting automated syndication...")
    posted_guids = load_posted()
    
    xml_data = fetch_rss()
    if not xml_data:
        return
        
    articles = parse_rss(xml_data)
    
    new_posts_found = False
    for article in articles:
        if article['guid'] not in posted_guids:
            print(f"New article found: {article['title']}")
            success = post_to_dev_to(article)
            if success:
                posted_guids.append(article['guid'])
                new_posts_found = True
            else:
                print(f"Skipping {article['guid']} due to error.")
                
    if new_posts_found:
        save_posted(posted_guids)
        print("State updated.")
    else:
        print("No new articles to syndicate.")

if __name__ == "__main__":
    main()
