file = open("followers.txt", "r")
follow_list = file.readlines()

for i in range(len(follow_list)):
    follow_list[i] = follow_list[i].strip()
file.close()
file = open("following.txt", "r")
following_list = file.readlines()

for i in range(len(following_list)):
    following_list[i] = following_list[i].strip()
file.close()

not_followed_list = []

for person in following_list:
    if person not in follow_list:
        not_followed_list.append(person)

for person in not_followed_list:
    print(person)

print(len(not_followed_list))


