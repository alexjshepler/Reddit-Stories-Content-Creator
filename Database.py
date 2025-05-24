import sqlite3 as sql

DB_NAME = 'posts.db'

# Create the database and the 'posts' table if it doesn't exist
def create_post_db():
    conn = sql.connect(DB_NAME)
    cursor = conn.cursor()

    """
    Create table if it doesn't exist
    
    Columns:
        - id | Post ID (TEXT, primary key, not null)
        - author | Author of the post, [deleted] if the author doesn't exist (TEXT, not null)
        - subreddit | The subreddit where the post was posted (TEXT, not null)
        - title | The title of the post (TEXT, not null)
        - content | The content of the post (TEXT, not null)
        - has_video | If a video has been generated for this post (BOOLEAN, default false)
        - video_path | The path to where the video is stored (TEXT, default null)
        - been_posted | If the video has been posted for this post (BOOLEAN, default false)
    """

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            author TEXT NOT NULL,
            subreddit TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            has_video BOOLEAN DEFAULT FALSE,
            video_path TEXT,
            been_posted BOOLEAN DEFAULT FALSE,
            timestamp INTEGER,
            score INTEGER,
            num_comments INTEGER,
            is_nsfw BOOLEAN DEFAULT FALSE
        )
        """
    )

    conn.commit()
    conn.close()


# Insert a new post
def insert_post(post):
    conn = sql.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO posts (
            id, author, subreddit, title, content,
            has_video, video_path, been_posted,
            timestamp, score, num_comments, is_nsfw
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            post["id"],
            post["author"],
            post["subreddit"],
            post["title"],
            post["content"],
            False,  # has_video
            None,  # video_path
            False,  # been_posted
            post.get("timestamp"),
            post.get("score"),
            post.get("num_comments"),
            post.get("is_nsfw", False),
        ),
    )

    conn.commit()
    conn.close()


def get_unused_posts():
    conn = sql.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM posts WHERE has_video = ?
        """,
        (False,),
    )

    posts = cursor.fetchall()
    conn.close()

    return posts
