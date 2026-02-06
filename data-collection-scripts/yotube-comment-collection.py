from yt_dlp import YoutubeDL
from youtube_comment_downloader import *
from itertools import islice
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd

nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

def label_sentiment(text):
    score = sia.polarity_scores(text)["compound"]

    if score >= 0.05:
        return "positive", score
    if score <= -0.05:
        return "negative", score
    else:
        return "neutral", score
    
ydl_opts = {
    "quiet": True,
    "extract_flat": True, 
}
categories = [
    "Gaming",
    "Movie",
    "Music",
    "Sports",
    "Education"
]

def get_video_urls(videos_per_category):
    videos = []
    with YoutubeDL(ydl_opts) as ydl:
        for category in categories:
            result = ydl.extract_info(f"ytsearch{videos_per_category}:{category}", download= False)
            
            for video in result.get("entries", []):                 
                url = video.get("url", [])
                if url:
                    videos.append({
                        "video_url": url,
                        "video_id": video.get("id", ""),
                        "category": category
                    })
                else:
                    print("No url found")

    return videos

def get_video_comments(videos, comments_req):
    dataset = []
    client = YoutubeCommentDownloader()

    for video in videos:
        comments = client.get_comments_from_url(video["video_url"], sort_by=SORT_BY_POPULAR)
        for comment in islice(comments, comments_req):
            text = comment.get("text", "")

            sentiment_label, sentiment_score = label_sentiment(text)

            dataset.append({
                "comment_id": comment.get("cid"),
                "video_id": video["video_id"],
                "video_url": video["video_url"],
                "video_category": video["category"],
                "comment_text": text,
                "sentiment_label": sentiment_label,
                "sentiment_score": sentiment_score,
                "like_count": comment.get("votes"),
                "reply_count": comment.get("reply_count"),
                "published_at": comment.get("time")
            })

    return dataset

videos = get_video_urls(videos_per_category=66)
data = get_video_comments(videos, comments_req=78)

df = pd.DataFrame(data)

df.to_csv("youtube_sentiment.csv", index=False)
print(len(data))
# print(data[0])