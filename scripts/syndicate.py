import os
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# Configuration
DEV_TO_API_URL = "https://dev.to/api/articles"
WP_API_URL = "https://aviperera.com/wp-json/wp/v2/posts"
STATE_FILE = "posted.json"

# Secrets
DEV_API_KEY = os.environ.get("DEV_API_KEY")

class HTMLFilter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data

def strip_tags(html):
    f = HTMLFilter()
    f.feed(html)
    return f.text

def load_posted():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted(posted_guids):
    with open(STATE_FILE, "w") as f:
        json.dump(posted_guids, f, indent=2)

def fetch_wp_posts(page=1, per_page=20):
    url = f"{WP_API_URL}?page={page}&per_page={per_page}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch WP posts on page {page}: {e}")
        return []

def post_to_dev_to(post):
    if not DEV_API_KEY:
        print("Error: DEV_API_KEY environment variable not set.")
        return False
        
    # WP API gives rendered HTML for title and content
    title = strip_tags(post['title']['rendered']).replace("&#8211;", "-").replace("&#8217;", "'")
    content = post['content']['rendered']
    link = post['link']
    post_id = str(post['id'])
    
    payload = {
        "article": {
            "title": title,
            "body_markdown": f"{content}\n\n*Originally published at [{title}]({link})*",
            "published": True,
            "canonical_url": link,
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
    print("Starting automated syndication with backfill...")
    posted_ids = load_posted()
    
    # Strategy: 
    # 1. Fetch page 1 (newest posts)
    # 2. If the newest post is NOT in posted_ids, publish it (priority to fresh content)
    # 3. If the newest post IS in posted_ids, we scan backwards through pages to find the oldest unposted article and publish just ONE to backfill.
    
    newest_posts = fetch_wp_posts(page=1)
    if not newest_posts:
        return
        
    # Check if the absolute newest post needs to be published
    newest_post = newest_posts[0]
    if str(newest_post['id']) not in posted_ids:
        print(f"Newest article found: {newest_post['title']['rendered']}")
        if post_to_dev_to(newest_post):
            posted_ids.append(str(newest_post['id']))
            save_posted(posted_ids)
        return

    print("No fresh articles today. Scanning archive for backfill...")
    
    # Backfill logic: scan pages until we find an unposted article
    # We want to publish the oldest unposted article we can find
    page = 1
    unposted_found = None
    
    while True:
        posts = fetch_wp_posts(page=page)
        if not posts:
            break # Reached the end of the blog
            
        for post in posts:
            if str(post['id']) not in posted_ids:
                # Keep tracking the oldest unposted we find
                unposted_found = post
                
        # If we reached a page where everything is posted but we found an unposted one earlier on the page, we break
        # Actually, we want to go as deep as possible to find the absolute oldest.
        page += 1

    if unposted_found:
        print(f"Backfilling archive article: {unposted_found['title']['rendered']}")
        if post_to_dev_to(unposted_found):
            posted_ids.append(str(unposted_found['id']))
            save_posted(posted_ids)
    else:
        print("Archive is completely fully syndicated!")

if __name__ == "__main__":
    main()
