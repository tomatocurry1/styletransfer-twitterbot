import tweepy
import time

print("Make sure you run main.py before running this test script.")
print("Also, set the time.sleep() value in twitter_component.py to something high (like 60) before running this.")

# Initialize some stuff
auth = tweepy.OAuthHandler("OoI0dqhS0j0JzHbv14fqvaSna", "T9h8zp0uEWElLffNjk4vkaDHUjkUTJjPY6CpnZFEm2OfPGUXV7")
auth.set_access_token("1304199818517123072-P6Pj4lxNXNowOG0NFXPnlEnujlbPBx", "L7oxgElytNmIkXwcfw5Vkoy7ROrvERMAFpGqiyi6e1eI0")
api = tweepy.API(auth)
tweets = []

# Send 21 requests to the bot
for x in range(0, 22):
    tweet = api.update_with_media("surfer.jpg", "@style_transfer udnie")
    print("Sent tweet with ID " + tweet.id_str)
    tweets.append(tweet)

# Give the bot a few seconds to respond
time.sleep(90)

# Make sure that the tweets were added onto the queue
for tweet in tweets[1:]:
    correct = False
    # Loop through the last 100 tweets sent by the bot
    for possible_response in api.user_timeline(count=100): # Check if this is the response that we're looking for
        if(possible_response.in_reply_to_status_id == tweet.id):
            # Check if the response was what we expected
            if(possible_response.text == "@style_transfer You have been added to the queue."):
                print("Tweet with ID " + tweet.id_str + " was added to the queue.")
                correct = True
                break
    # If the correct response was not sent back to the tweet
    if(not correct):
        print("Tweet with ID " + tweet.id_str + " did not have the correct response!")

# Make sure that the last tweet was not added onto the queue
tweet = tweets[0]
correct = False
# Loop through the last 100 tweets sent by the bot
for possible_response in api.user_timeline(count=100):
    # Check if this is the response that we're looking for
    if(possible_response.in_reply_to_status_id == tweet.id):
        # Check if the response was what we expected
        if(possible_response.text == "@style_transfer Sorry, I currently have too many requests in my queue. Your request cannot be completed."):
            print("Tweet with ID " + tweet.id_str + " was not added onto the queue.")
            correct = True
            break

if(not correct):
    print("Tweet with ID " + tweet.id_str + " did not have the correct response!")
