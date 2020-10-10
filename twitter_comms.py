import tweepy
import time
import requests
import re

# Authenticate to Twitter
# It's definitely not considered secure to just leave API keys hanging around in source code, but whatever
auth = tweepy.OAuthHandler("Xuu8AlgNIdcnD3XeWUc325mId", "zlzjJp4B783U1KzYaAJBWykYfk6haihCr1i8czNTAdEKlgy42W")
auth.set_access_token("1304199818517123072-tCRZLdNkX7GFtafjyUdZJHSr47t6uT", "YFbTORPAaw3XTy2L9BYIJpaKa7xwhXm53s7kmT0mtYrlL")
api = tweepy.API(auth)

# Check for a new Tweet every five minutes
while True:
    # Problem: What if multiple users mention the bot within five minutes? The call to
    # api.mentions_timeline(count=1) will only return the last mention sent to us. If we
    # instead called api.mentions_timeline(), it would return every single mention, but
    # that list might get huge and we don't want to sift through every single mention.

    # Problem: When we call api.mentions_timeline(), it returns all mentions, if we call
    # api.mentions_timeline(count=1), it returns the last mention. How do we know whether
    # the last mention has already been replied to or not? It is possible that nobody
    # used the bot in the last five minutes, which means that 

    # Get the last mention
    mention = api.mentions_timeline(count=1)[0]
    try:
        # Get the URL for the image inside of the mention
        link = mention.entities["media"][0]["media_url_https"]

        # Download the image using the requests library
        with requests.get(link, stream=True) as response:
            with open("temp.jpg", "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        # TODO: If the image was downloaded successfully, call the style transfer component.
        # TODO: If the style transfer worked, send an image back to the user.

    except KeyError:
        # If there was no image in the mention, then a KeyError will be thrown and we do nothing.
        pass

    # TODO: Delete the "time.sleep(5*60)" line once the style transfer is working.
    # 
    # I only made the program sleep for five minutes because I didn't want a million API calls a
    # second the very first time I ran this program (because that would get us banned by Twitter
    # pretty fast). Once the style transfer component works, this will no longer be an issue because
    # the style transfer will take a long time anyways. This line should be deleted after the
    # style transfer stuff is working.
    time.sleep(5*60)
