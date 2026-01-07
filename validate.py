import json

with open("dontfollowback.json", "r") as not_followers_file:
    not_followers = json.load(not_followers_file)
with open("celebrities.json", "r") as celebrities_file:
    celebrities = json.load(celebrities_file)
    celebrities_usernames = [x["username"] for x in celebrities]

for account in not_followers["dontFollowMeBack"]:
    if account["username"] not in celebrities_usernames:
        print()
        print("Not a celebrity")
        print("Username:", account["username"])
        print("Name:", account["full_name"])
        print("Link:", f"https://www.instagram.com/{account["username"]}/")
        inp = input("Add this to celebrity (y/n) or s to stop till here: ")
        if inp == "y":
            celebrities.append(account)
            print("Celebrity Added")
            print()
        elif inp == "s":
            with open("celebrities.json", "w") as celebrities_file:
                json.dump(celebrities, celebrities_file, indent=2)
                print("Celebrities Updated")
            exit()
        else:
            continue
with open("celebrities.json", "w") as celebrities_file:
    json.dump(celebrities, celebrities_file, indent=2)
    print("Celebrities Updated")
