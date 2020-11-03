import threading
import multiprocessing
import time
import tweepy
import requests
import datetime
import queue

class TwitterComponent:
    api = None # Used to access the Twitter API
    api_lock = None # Lock that must be acquired before using the api
    twitter_queue = None # Queue for Twitter Statuses
    TIMEOUT = 20*60 # Max timeout in seconds (equal to twenty minutes)

    def __init__(self):
        self.twitter_queue = queue.Queue()
        self.api_lock = threading.Lock()
        auth = tweepy.OAuthHandler("OoI0dqhS0j0JzHbv14fqvaSna", "T9h8zp0uEWElLffNjk4vkaDHUjkUTJjPY6CpnZFEm2OfPGUXV7")
        auth.set_access_token("1304199818517123072-P6Pj4lxNXNowOG0NFXPnlEnujlbPBx", "L7oxgElytNmIkXwcfw5Vkoy7ROrvERMAFpGqiyi6e1eI0")
        self.api_lock.acquire(blocking=True)
        self.api = tweepy.API(auth)
        self.api_lock.release()

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

            # Delete the mentions in the list that come before last_time
            not_deleted_mentions = []
            for mention in mentions:
                if(mention.created_at > last_time):
                    not_deleted_mentions.append(mention)
            mentions = not_deleted_mentions

            # TODO: Do input validation for mentions.
            # Delete mentions that do not have a valid image or do not have a name of a style

            if(len(mentions) > 0):
                # Set last_time equal to the created_at value for the latest mention
                last_time = mentions[0].created_at

                print("Enqueue Thread: Adding mentions to the queue.")
                for mention in mentions:
                    user_to_reply_to = mention.user.screen_name
                    if(self.twitter_queue.qsize() > 20):
                        # Send a Tweet to the user that they weren't added to the queue
                        print("Enqueue Thread: Rejected " + user_to_reply_to + "\'s request.")
                        self.api_lock.acquire()
                        self.api.update.status("@" + user_to_reply_to + " Sorry, I currently have too many requests in my queue. Your request cannot be completed.")
                        self.api_lock.release()
                    else:
                        print("Enqueue Thread: Accepted " + user_to_reply_to + "\'s request.")
                        self.api_lock.acquire()
                        self.api.update_status("@" + user_to_reply_to + " you have been added to the queue.", in_reply_to_status_id=mention.id)
                        self.api_lock.release()
                        self.twitter_queue.put(mention)

            # Wait for 20 seconds
            print("Enqueue Thread: Waiting.")
            time.sleep(20)

    # Dequeues a mention and executes the style transfer thread
    # If there are no mentions, then this will wait until there is a mention
    def __prune_queue(self, none):
        assert threading.current_thread().name == "dequeue_thread"
        time.sleep(3)
        for mention in iter(self.twitter_queue.get, None):
            print(mention.text)

        """

        TODO: This function can only be written after the queue has been finished.
        It should do the following:
        1.) If the queue is empty, block the thread until it is not empty.
        2.) Dequeue an item on the queue.
        3.) Call the style transfer component in another process.
            > Use something like: p = multiprocessing.Process(target=StyleTransfer.transfer, name="style_transfer", args=args)
            > Then start it with p.start()
        4.) Use p.join(timeout=TIMEOUT) to wait for the style transfer process.
        5.) Check if the style transfer thread is alive (use p.is_alive()).
        6.) If it's still alive after twenty minutes, kill it with p.terminate()
        7.) Go back to step one and repeat.

        """
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
