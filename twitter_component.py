import threading
import multiprocessing
import time
import tweepy
import requests
import datetime
import queue
import os
from style_component import StyleComponent

class TwitterComponent:
    api = None # Used to access the Twitter API
    api_lock = None # Lock that must be acquired before using the api
    twitter_queue = None # Queue for Twitter Statuses
    style_component = None # Access the Style Component
    TIMEOUT = 20*60 # Max timeout in seconds (equal to twenty minutes)

    def __init__(self):
        self.twitter_queue = queue.Queue()
        self.api_lock = threading.Lock()
        auth = tweepy.OAuthHandler("OoI0dqhS0j0JzHbv14fqvaSna", "T9h8zp0uEWElLffNjk4vkaDHUjkUTJjPY6CpnZFEm2OfPGUXV7")
        auth.set_access_token("1304199818517123072-P6Pj4lxNXNowOG0NFXPnlEnujlbPBx", "L7oxgElytNmIkXwcfw5Vkoy7ROrvERMAFpGqiyi6e1eI0")
        self.api_lock.acquire(blocking=True)
        self.api = tweepy.API(auth)
        self.api_lock.release()
        self.style_component = StyleComponent()

    # Returns a new list of mentions that does not contain invalid requests
    def __validate(self, mentions, last_time):
        assert threading.current_thread().name == "enqueue_thread"
        not_deleted_mentions = []

        # Do input validation for all mentions
        for mention in mentions:
            delete = False

            # Get the user's screen name
            user_to_reply_to = mention.user.screen_name

            # Delete the mentions in the list that come before last_time
            if(mention.created_at <= last_time):
                delete = True

            # Delete the mentions that do not contain any image
            try:
                # If there is no image, this line of code will throw a KeyError
                mention.entities["media"][0]
            except KeyError:
                # Send a message to the user saying that they need to attach an image
                self.api_lock.acquire()
                self.api.update_status("@" + user_to_reply_to + " You must attach an image.",
                        in_reply_to_status_id=mention.id)
                self.api_lock.release()
                delete = True

            # Check the style transfer name
            add = False
            for style in self.style_component.styleImages: # Loop through each style
                if(style in mention.text): # Check if the name of that style appeared in the text
                    add = True
                    mention.text = style # This is just done to make it easier to the dequeue thread
                    break
            if(not add): # If the user did not have a style, then do this
                self.api_lock.acquire()
                self.api.update_status("@" + user_to_reply_to + " Invalid style. Your options are: "
                        + str(list(self.style_component.styleImages.keys()))[1:-1],
                        in_reply_to_status_id=mention.id)
                self.api_lock.release()
                delete = True

            # Add the mention if it passed all the checks
            if(not delete):
                not_deleted_mentions.append(mention)

        return not_deleted_mentions

    # Checks for mentions and enqueues them if necessary
    def __check_mentions(self, none):
        assert threading.current_thread().name == "enqueue_thread"

        # This contains the last time that we checked for mentions
        last_time = datetime.datetime.min

        while True:
            # Get the last 20 mentions
            print("Enqueue Thread: Reading last 20 mentions.")
            self.api_lock.acquire(blocking=True)
            mentions = self.api.mentions_timeline(count=20)
            self.api_lock.release()

            # Validate the mentions
            mentions = self.__validate(mentions, last_time)

            if(len(mentions) > 0):
                # Set last_time equal to the created_at value for the latest mention
                last_time = mentions[0].created_at

                print("Enqueue Thread: Adding " + str(len(mentions)) + " mentions to the queue.")
                for mention in mentions:
                    user_to_reply_to = mention.user.screen_name
                    if(self.twitter_queue.qsize() > 20):
                        # Send a Tweet to the user that they weren't added to the queue
                        print("Enqueue Thread: Rejected " + user_to_reply_to + "\'s request.")
                        self.api_lock.acquire()
                        self.api.update_status("@" + user_to_reply_to + " Sorry, I currently have too many requests in my queue. Your request cannot be completed.", in_reply_to_status_id=mention.id)
                        self.api_lock.release()
                    else:
                        print("Enqueue Thread: Accepted " + user_to_reply_to + "\'s request.")
                        self.api_lock.acquire()
                        self.api.update_status("@" + user_to_reply_to + " You have been added to the queue.", in_reply_to_status_id=mention.id)
                        self.api_lock.release()
                        self.twitter_queue.put(mention)

            # Wait for 20 seconds
            print("Enqueue Thread: Waiting.")
            time.sleep(20)

    # Dequeues a mention and executes the style transfer thread
    # If there are no mentions, then this will wait until there is a mention
    def __prune_queue(self, none):
        assert threading.current_thread().name == "dequeue_thread"

        while True:
            # Get the mention from the queue
            print("Dequeue Thread: Waiting for mention in queue.")
            mention = self.twitter_queue.get(block=True)
            user_to_reply_to = mention.user.screen_name
            print("Dequeue Thread: Processing request from " + user_to_reply_to)

            try:
                # Download the image
                link = mention.entities["media"][0]["media_url_https"]
                with requests.get(link, stream=True) as response:
                    with open("temp.jpg", "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                print("Dequeue Thread: Successfully downloaded " + user_to_reply_to + "\'s image and starting style transfer.")

                # Create a new process for the style transfer
                images=("temp.jpg", self.style_component.styleImages[mention.text])
                style_transfer_process = multiprocessing.Process(target=self.style_component.transfer,
                        name="style_transfer", args=images)
                style_transfer_process.start()
                style_transfer_process.join(timeout=self.TIMEOUT)

                # Delete the image
                os.remove("temp.jpg")

                # Kill the process if it's alive after the timeout
                if(style_transfer_process.is_alive()):
                    print("Dequeue Thread: Style transfer took more than 20 minutes!")
                    style_transfer_process.terminate()
                    self.api_lock.acquire()
                    self.api.update_status("@" + user_to_reply_to + " I could not process your style transfer because it was taking too long :(", in_reply_to_status_id=mention.id)
                    self.api_lock.release()
                else:
                    # Tweet the output
                    print("Dequeue Thread: Finished style transfer for " + user_to_reply_to)
                    self.api_lock.acquire()
                    self.api.update_with_media("output.jpg",
                            "@" + user_to_reply_to + " Here is your finished image!",
                            in_reply_to_status_id=mention.id)
                    self.api_lock.release()
            except KeyError:
                # If there was no image in the mention, then a KeyError will be thrown
                pass

    # Starts two threads: one for enqueuing Tweets and another for dequeuing
    def start(self):
        try:
            arg = []
            arg.append(self)
            enqueue_thread = threading.Thread(target=self.__check_mentions, name="enqueue_thread", args=arg)
            dequeue_thread = threading.Thread(target=self.__prune_queue, name="dequeue_thread", args=arg)
            enqueue_thread.start()
            dequeue_thread.start()
        except Exception as e:
            print("Error: Unable to start threads.")
            print(e)
