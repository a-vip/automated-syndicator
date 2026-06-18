import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration
DEV_TO_API_URL = "https://dev.to/api/articles"
RSS_FEED_URL = "https://aviperera.com/feed/"
STATE_FILE = "posted.json"
BLOGGER_BLOG_ID = "7370356485249616409"

# Secrets
DEV_API_KEY = os.environ.get("DEV_API_KEY")
GOOGLE_OAUTH_TOKEN_JSON = os.environ.get("GOOGLE_OAUTH_TOKEN_JSON")

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

def fetch_rss_page(page=1):
    url = f"{RSS_FEED_URL}?paged={page}" if page > 1 else RSS_FEED_URL
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            return parse_rss(xml_data)
    except Exception as e:
        print(f"Failed to fetch RSS page {page}: {e}")
        return []

def parse_rss(xml_data):
    try:
        root = ET.fromstring(xml_data)
        articles = []
        for item in root.findall('./channel/item'):
            guid = item.find('guid').text
            title = item.find('title').text
            link = item.find('link').text
            
            content_elem = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            if content_elem is not None:
                content = content_elem.text
            else:
                desc_elem = item.find('description')
                content = desc_elem.text if desc_elem is not None else ""
                
            articles.append({
                'id': guid, # Using guid as ID
                'title': title,
                'link': link,
                'content': content
            })
        return articles
    except Exception as e:
        print(f"Error parsing RSS XML: {e}")
        return []

def post_to_dev_to(post):
    if not DEV_API_KEY:
        print("Error: DEV_API_KEY environment variable not set.")
        return False
        
    title = strip_tags(post['title']).replace("&#8211;", "-").replace("&#8217;", "'")
    content = post['content']
    link = post['link']
    
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

def post_to_blogger(post):
    if not GOOGLE_OAUTH_TOKEN_JSON:
        print("Error: GOOGLE_OAUTH_TOKEN_JSON environment variable not set.")
        return False
        
    try:
        creds_data = json.loads(GOOGLE_OAUTH_TOKEN_JSON)
        creds = Credentials.from_authorized_user_info(creds_data)
        service = build('blogger', 'v3', credentials=creds)
        
        title = strip_tags(post['title']).replace("&#8211;", "-").replace("&#8217;", "'")
        content = post['content']
        link = post['link']
        
        html_content = f'{content}<br><hr><p><em>Originally published at <a href="{link}">{title}</a>.</em></p>'
        
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": html_content
        }
        
        posts = service.posts()
        request = posts.insert(blogId=BLOGGER_BLOG_ID, body=body, isDraft=False)
        response = request.execute()
        
        print(f"Successfully posted to Blogger: {response.get('url')}")
        return True
    except Exception as e:
        print(f"Exception while posting to Blogger: {e}")
        return False

def main():
    print("Starting automated syndication with backfill (via RSS)...")
    posted_ids = load_posted()
    
    newest_posts = fetch_rss_page(page=1)
    if not newest_posts:
        return
        
    newest_post = newest_posts[0]
    if newest_post['id'] not in posted_ids:
        print(f"Newest article found: {newest_post['title']}")
        dev_success = post_to_dev_to(newest_post)
        blogger_success = post_to_blogger(newest_post)
        
        if dev_success or blogger_success:
            posted_ids.append(newest_post['id'])
            save_posted(posted_ids)
        return

    print("No fresh articles today. Scanning archive for backfill...")
    
    page = 1
    unposted_found = None
    
    while True:
        posts = fetch_rss_page(page=page)
        if not posts:
            break
            
        for post in posts:
            if post['id'] not in posted_ids:
                unposted_found = post
                
        page += 1

    if unposted_found:
        print(f"Backfilling archive article: {unposted_found['title']}")
        dev_success = post_to_dev_to(unposted_found)
        blogger_success = post_to_blogger(unposted_found)
        
        if dev_success or blogger_success:
            posted_ids.append(unposted_found['id'])
            save_posted(posted_ids)
    else:
        print("Archive is completely fully syndicated!")

if __name__ == "__main__":
    main()
