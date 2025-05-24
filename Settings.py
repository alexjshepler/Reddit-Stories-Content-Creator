import json

import praw # Reddit

SETTINGS_PATH = './settings.json'

# ========== LOAD SETTINGS ==========

def load_settings():
    settings = {}

    print("========== Loading Settings ==========")

    # Try to lad the settings from file
    try:
        with open(SETTINGS_PATH, 'r') as file:
            settings = json.load(file)

        print('Loaded settings')
    except FileNotFoundError:
        print('Settings not found, lets create them')
    except Exception as ex:
        print(f'Something really went wrong for you to get here. This is the error that I got:\n{ex}')

    # Create new settings if settings don't exist
    if not settings:
        settings = prompt_settings()

    # Validate settings
    settings = validate_settings(settings)

    with open(SETTINGS_PATH, 'w') as file:
        json.dump(settings, file, indent=4)

    return settings

# ========== GET SETTINGS ==========

def prompt_settings():
    settings = {}

    print("========== Getting Settings ==========")

    client_id, client_secret, username, subreddits, min_words, min_comments, min_ratio = prompt_reddit()
    # TODO Get TTS and video settings

    settings = {
        "reddit": {
            "api": {
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username
            },
            "subreddits": subreddits,
            "min_words": min_words,
            "min_comments": min_comments,
            "min_ratio": min_ratio
        }
    }

    return validate_settings(settings)


def prompt_reddit():
    print("\n===== Reddit Settings\n")

    print("First, go to: https://www.reddit.com/prefs/apps\n")

    while True:
        has_app = input("Do you have an app created on Reddit? (y/n): ").lower()

        if has_app in ["y", "n"]:
            break
        else:
            print("Please only enter y or n\n")

    # Guide the user through the process of creating an app on Reddit
    if has_app == "n":
        print("\nLet's create one! Follow these steps:")
        print(
            """
        1) Go to 'are you a developer? Create an app...'
        2) Enter any name for your app, select 'script', and use any valid redirect URI (e.g., https://google.com).
        3) Complete the captcha and click 'Create app'.
        4) Once created, click 'edit app' to see your app details.
        """
        )

    print("----- Reddit Settings")
    # Collect app details
    client_id = input(
        'Enter the app id (under the app name, next to "personal use script"): '
    )
    client_secret = input("Enter the app secret: ")
    username = input("Enter your Reddit username: ")

    # Get the minimum amount of words for the post
    while True:
        user_input = input("Enter the minimum amount of words for the post: ")

        try:
            min_words = int(user_input)
            if min_words >= 0:
                break
            else:
                print("Please enter a number greater than 0")
        except:
            print("Please enter a number")

    # Get the minimum amount of comments on a post
    while True:
        user_input = input("Enter the minimum amount of comments for the post: ")

        try:
            min_comments = int(user_input)
            if min_comments >= 0:
                break
            else:
                print("Please enter a number greater than 0")
        except:
            print("Please enter a number")

    # Get the minimum upvote ratio
    while True:
        user_input = input("Enter the minimum upvote ratio for the post: ")

        try:
            min_ratio = int(user_input)
            break
        except:
            print("Please enter a number")

    # Collect subreddits
    subreddits = prompt_subreddits()

    return client_id, client_secret, username, subreddits, min_words, min_comments, min_ratio


def prompt_subreddits():
    subreddits = []

    print("\n----- Subreddits")
    print(
        "You can enter subreddit names or linkes, separated by commas, or enter one subreddit at a time"
    )
    print("To stop, type '!q' or just press enter on an empty line")

    # Get subreddits
    while True:
        sub_input = input("Enter subreddit(s): ")

        if sub_input.lower() == "!q" or sub_input == "":
            break

        # Check if input has multiple subreddits
        if "," in sub_input:
            subreddits.extend([item.strip() for item in sub_input.split(",")])
        else:
            subreddits.append(sub_input.strip())

    # Normalize subreddits
    subreddits = [
        sub.replace("https://www.reddit.com/r/", "")
        .replace("www.reddit.com/r/", "")
        .replace("reddit.com/r/", "")
        .replace("/r/", "")
        .replace("/", "")
        .strip()
        for sub in subreddits
    ]

    print("Subreddits to fetch from")
    for i in subreddits:
        print(f"\t- {i}")

    return subreddits


# ========== VALIDATE SETTINGS ==========


def validate_settings(settings):
    print("========== Validating Settings ==========")

    # Reddit Settings
    reddit_settings = settings.get("reddit", {})
    reddit_api_settings = reddit_settings.get("api", {})

    client_id = reddit_api_settings.get("client_id")
    client_secret = reddit_api_settings.get("client_secret")
    username = reddit_api_settings.get("username")
    subreddits = reddit_settings.get("subreddits")
    min_words = reddit_settings.get("min_words")
    min_comments = reddit_settings.get("min_comments")
    min_ratio = reddit_settings.get("min_ratio")

    client_id, client_secret, username, subreddits, min_words, min_comments = (
        validate_reddit(
            client_id, client_secret, username, subreddits, min_words, min_comments
        )
    )

    settings = {
        "reddit": {
            "api": {
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username
            },
            "subreddits": subreddits,
            "min_words": min_words,
            "min_comments": min_comments,
            "min_ratio": min_ratio
        }
    }

    return settings


def validate_reddit(
    client_id, client_secret, username, subreddits, min_words, min_comments
):
    isValid = False

    while not isValid:
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                user_agent="RedditAppValidator",
            )

            reddit.subreddit("AITAH").id
            isValid = True
        except Exception as ex:
            print(f"Error: Reddit settings are invalid or missing. {ex}")

            client_id, client_secret, username, subreddits, min_words, min_comments = (
                prompt_reddit()
            )

    valid_subreddits = []

    for sub in subreddits:
        if sub:
            try:
                reddit.subreddit(sub).id
                valid_subreddits.append(sub)
                print(f"Valid subreddit: {sub}")
            except Exception as ex:
                print("Warning: Subreddit '{sub}' is invalid. Error: {ex}")

    return client_id, client_secret, username, valid_subreddits, min_words, min_comments
