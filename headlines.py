import feedparser
import json
import redis
import os

RSS_FEED_URL = 'http://www.domaining.com/rss/'
r = redis.from_url(os.environ["REDIS_URL"])


def fetch_rss_feed(url):
    return feedparser.parse(url)


def check_for_all_posts(feed):
    all_posts = feed.entries
    return all_posts


def parsed_headlines():
    rss_feed = fetch_rss_feed(RSS_FEED_URL)
    posts = check_for_all_posts(rss_feed)
    parsed_headlines = []
    for post in posts:
        record = {}
        record['title'] = post.title
        record['link'] = post.link
        record['published'] = post.published
        parsed_headlines.append(record)
    return parsed_headlines


def get_updated_headlines(new, previous):
    if previous:
        previous_set = {(item['title'], item['link'], item['published'])
                        for item in previous}
    else:
        previous_set = set()
    new_set = {(item['title'], item['link'], item['published'])
                        for item in new}
    updated_set = new_set - previous_set
    updated = [{'title': t, 'link': l, 'published': p}
               for t, l, p in updated_set]
    return updated

if __name__ == "__main__":
    previous_headlines = r.get('feed')
    if previous_headlines:
        previous_headlines = json.loads(previous_headlines)
    new_headlines = parsed_headlines()
    updated_headlines = get_updated_headlines(new_headlines, previous_headlines)
    if updated_headlines:
        headlines_stack = r.get('headlines')
        if headlines_stack:
            output_headlines = json.loads(headlines_stack)
            if len(output_headlines) >= 40:
                output_headlines = output_headlines[20:]
            output_headlines = output_headlines + list(reversed(updated_headlines))
            r.set('headlines', json.dumps(output_headlines))
            r.set('feed', json.dumps(new_headlines))
        else:
            output_headlines = list(reversed(updated_headlines))
            r.set('headlines', json.dumps(output_headlines))
            r.set('feed', json.dumps(new_headlines))
