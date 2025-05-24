import time

import praw
import prawcore

from praw.models import Submission

from Database import insert_post

class Reddit:
    def __init__(self, settings):
        reddit_settings = settings.get("reddit", {})
        reddit_api_settings = reddit_settings.get("api")

        self.reddit = praw.Reddit(
            client_id=reddit_api_settings.get("client_id"),
            client_secret=reddit_api_settings.get("client_secret"),
            username=reddit_api_settings.get("username"),
            user_agent="RedditAppBot",
        )

        self.subreddits = reddit_settings.get("subreddits")
        self.min_words = reddit_settings.get("min_words")
        self.min_comments = reddit_settings.get("min_comments")
        self.min_ratio = reddit_settings.get("min_ratio")

    def fetch_all_posts(self):
        for sub in self.subreddits:
            subreddit = self.reddit.subreddit(sub)

            retries = 15
            attempt_num = 1
            last_post = None
            post_count = 0

            while True:
                try:
                    posts = subreddit.new(limit=100, params={"after": last_post})

                    batch_count = 0

                    for post in posts:
                        post: Submission

                        last_post = post.name
                        
                        # Filtering
                        if not post.is_self:
                            continue

                        if len(post.selftext.split(" ")) < self.min_words:
                            continue

                        if post.num_comments < self.min_comments:
                            continue

                        if post.upvote_ratio < self.min_ratio:
                            continue

                        author = post.author.name if post.author else "[deleted]"

                        post_data = {
                            "id": post.id,
                            "author": author,
                            "subreddit": sub,
                            "title": post.title,
                            "content": post.selftext,
                            "timestamp": int(post.created_utc),
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "is_nsfw": post.over_18
                        }

                        insert_post(post_data)
                        batch_count += 1
                        post_count += 1

                    if batch_count == 0:
                        print(f"Finished fetching all available posts from r/{sub}")
                        break

                    print(
                        f"Fetched {batch_count} more posts from r/{sub}, total: {post_count}"
                    )

                    time.sleep(2)

                except prawcore.exceptions.RequestException as ex:
                    print(
                        f"Reddit API request failed ({ex}). Retrying in {5 * attempt_num} seconds..."
                    )
                    time.sleep(5 * attempt_num)
                    retries += 1

                except prawcore.exceptions.ServerError as ex:
                    print(
                        f"Reddit server error ({ex}). Retrying in {10 * attempt_num} seconds..."
                    )
                    time.sleep(10 * attempt_num)
                    retries += 1

                except Exception as ex:
                    print(f"Unexpected error: {ex}")
                    break
