# Get instance
import instaloader
from getpass import getpass

L = instaloader.Instaloader()

import os
os.system('rm followers.txt following.txt')

# Login or load session
username = input("Username: ")
password = getpass('Password:')
L.login(username, password)  # (login)

# Obtain profile metadata
profile = instaloader.Profile.from_username(L.context, username)

# Print list of followees
follow_list = []
followee_list = []
count = 0
for followee in profile.get_followers():
    follow_list.append(followee.username)
    file = open("followers.txt", "a+")
    file.write(followee.username)
    file.write("\n")
    file.close()
    print(count, followee.username)
    count = count + 1
# (likewise with profile.get_followers())
count = 0
for followee in profile.get_followees():
    followee_list.append(followee.username)
    file = open("following.txt", "a+")
    file.write(followee.username)
    file.write("\n")
    file.close()
    print(count, followee.username)
    count = count + 1

print(len(follow_list))
print(len(followee_list))