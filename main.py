from Database import create_post_db
from Settings import load_settings
from Reddit import Reddit
from Generate import generate_videos

def main():
    create_post_db()

    settings = load_settings()
    reddit = Reddit(settings)

    reddit.fetch_all_posts()

    generate_videos(settings)

if __name__ == '__main__':
    main()