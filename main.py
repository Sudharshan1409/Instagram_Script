import json
import os
import time

import requests

# --- CONFIGURATION ---
# Before running, you need to provide your Instagram username.

# 1. Your Instagram username
USERNAME = "this.user.sud"

# 2. Your Instagram Session ID.
#    This will be prompted for when you run the script, or you can set it
#    as an environment variable named INSTAGRAM_SESSION_ID.
#    If you set it as an environment variable, the script will use that
#    value and will not prompt you.

# --- CONSTANTS ---
BASE_URL = "https://www.instagram.com"
GRAPHQL_URL = f"{BASE_URL}/graphql/query/"
USER_SEARCH_URL = f"{BASE_URL}/web/search/topsearch/"

FOLLOWERS_QUERY_HASH = "c76146de99bb02f6415203be841dd25a"
FOLLOWING_QUERY_HASH = "d04b0a864b4b54837c0d870b0e77e076"

CELEBRITIES_FILE = "celebrities.json"
HISTORY_FILE = "followers_history.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
}
# COOKIES will be set dynamically with the session ID
COOKIES = {}

# --- HELPER FUNCTIONS ---


def load_json_file(file_path, default_data=None):
    """Loads a JSON file if it exists, otherwise returns default data."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_data if default_data is not None else []


def save_json_file(file_path, data):
    """Saves data to a JSON file with pretty printing."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_user_id(username):
    """Fetches the user ID for a given username."""
    print(f"Fetching user ID for {username}...")
    try:
        response = requests.get(
            f"{USER_SEARCH_URL}?query={username}", headers=HEADERS, cookies=COOKIES
        )
        response.raise_for_status()
        data = response.json()
        if data["users"]:
            user_id = data["users"][0]["user"]["pk"]
            print(f"Found user ID: {user_id}")
            return user_id
        else:
            print("User not found.")
            return None
    except requests.RequestException as e:
        print(f"Error fetching user ID: {e}")
        return None


def get_users(user_id, query_hash, list_name):
    """Fetches a list of users (followers or following) for a given user ID."""
    print(f"Fetching {list_name} list...")
    users = []
    after = None
    has_next = True

    while has_next:
        variables = {
            "id": user_id,
            "include_reel": True,
            "fetch_mutual": True,
            "first": 50,
        }
        if after:
            variables["after"] = after

        try:
            response = requests.get(
                GRAPHQL_URL,
                params={"query_hash": query_hash, "variables": json.dumps(variables)},
                headers=HEADERS,
                cookies=COOKIES,
            )
            response.raise_for_status()
            data = response.json()["data"]["user"]

            if list_name == "followers":
                page_info = data["edge_followed_by"]["page_info"]
                edges = data["edge_followed_by"]["edges"]
            else:  # following
                page_info = data["edge_follow"]["page_info"]
                edges = data["edge_follow"]["edges"]

            has_next = page_info["has_next_page"]
            after = page_info["end_cursor"]

            for node in edges:
                users.append(
                    {
                        "username": node["node"]["username"],
                        "full_name": node["node"]["full_name"],
                    }
                )

            print(f"  - Fetched {len(users)} {list_name} so far...")
            # Respectful delay to avoid rate limiting
            time.sleep(1)

        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            if "login_required" in response.text:
                print(
                    "Error: Login required. Your SESSION_ID might be invalid or expired."
                )
            break
        except KeyError:
            print("Error parsing response. The Instagram API might have changed.")
            break

    print(f"Finished fetching. Total {list_name}: {len(users)}")
    return users


def track_unfollowers(current_followers):
    """Compares current followers with historical data to find unfollowers."""
    print("\n--- Checking for Unfollowers ---")
    previous_followers_data = load_json_file(HISTORY_FILE, {"followers": []})
    previous_followers = {
        user["username"] for user in previous_followers_data["followers"]
    }
    current_followers_set = {user["username"] for user in current_followers}

    unfollowers = previous_followers - current_followers_set
    new_followers = current_followers_set - previous_followers

    if not previous_followers:
        print(
            "No previous follower data found. Saving current followers for next time."
        )
    else:
        if unfollowers:
            print("You have been unfollowed by:")
            for user in unfollowers:
                print(f"  - {user}")
        else:
            print("No one has unfollowed you since the last check. Good job!")

        if new_followers:
            print("\nNew followers:")
            for user in new_followers:
                print(f"  - {user}")
        else:
            print("No new followers since the last check.")

    # Save current state for next run
    save_json_file(HISTORY_FILE, {"followers": current_followers})
    print("Follower history has been updated.")


def validate_non_followers(dont_follow_back):
    """Interactive validation for users who don't follow back."""
    print("\n--- Validating Users Who Don't Follow You Back ---")
    celebrities = load_json_file(CELEBRITIES_FILE)
    celebrity_usernames = {celeb["username"] for celeb in celebrities}

    updated = False
    for account in dont_follow_back:
        if account["username"] not in celebrity_usernames:
            print("\n----------------------------------------")
            print(f"User: {account['full_name']} (@{account['username']})")
            print(f"Link: {BASE_URL}/{account['username']}/")

            inp = input(
                "Add this user to your 'celebrities' list? (y/n/s to stop): "
            ).lower()

            if inp == "y":
                celebrities.append(account)
                celebrity_usernames.add(account["username"])
                updated = True
                print(f"Added {account['username']} to celebrities.")
            elif inp == "s":
                print("Stopping validation.")
                break
            else:
                print(f"Skipping {account['username']}.")

    if updated:
        # Sort celebrities by username for consistency
        celebrities.sort(key=lambda x: x["username"])
        save_json_file(CELEBRITIES_FILE, celebrities)
        print("\nCelebrities file has been updated.")
    else:
        print("\nNo new celebrities were added.")


def main():
    """Main function to run the script."""
    global COOKIES # Declare COOKIES as global to modify it

    session_id = os.getenv("INSTAGRAM_SESSION_ID")
    if not session_id:
        print("\n--- Instagram Session ID Required ---")
        print("To get your session ID, follow the instructions in the README.md or at the top of this script.")
        session_id = input("Please enter your Instagram session ID: ").strip()
        if not session_id:
            print("Error: Session ID cannot be empty. Exiting.")
            return
    
    COOKIES["sessionid"] = session_id

    user_id = get_user_id(USERNAME)
    if not user_id:
        return

    # Fetch followers and following lists
    followers = get_users(user_id, FOLLOWERS_QUERY_HASH, "followers")
    time.sleep(5)  # Extra delay between big operations
    following = get_users(user_id, FOLLOWING_QUERY_HASH, "following")

    if not followers or not following:
        print("\nCould not fetch follower or following lists. Exiting.")
        return

    # Track unfollowers
    track_unfollowers(followers)

    # Find who doesn't follow back
    follower_usernames = {user["username"] for user in followers}
    dont_follow_back = [
        user for user in following if user["username"] not in follower_usernames
    ]

    print(f"\nFound {len(dont_follow_back)} users who don't follow you back.")

    # Validate and manage celebrities
    validate_non_followers(dont_follow_back)

    print("\nProcess finished successfully!")


if __name__ == "__main__":
    main()
