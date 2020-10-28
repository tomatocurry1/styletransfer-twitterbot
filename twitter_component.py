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
    TIMEOUT = 20*60 # Max timeout in seconds (equal to twenty minutes)

    def __init__(self):
        self.api_lock = threading.Lock()
        self.api_lock.acquire(blocking=True)
        auth = tweepy.OAuthHandler("Xuu8AlgNIdcnD3XeWUc325mId", "zlzjJp4B783U1KzYaAJBWykYfk6haihCr1i8czNTAdEKlgy42W")
        auth.set_access_token("1304199818517123072-tCRZLdNkX7GFtafjyUdZJHSr47t6uT", "YFbTORPAaw3XTy2L9BYIJpaKa7xwhXm53s7kmT0mtYrlL")
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

            if(len(mentions) > 0):
                # Set last_time equal to the created_at value for the latest mention
                last_time = mentions[0].created_at

                print("Enqueue Thread: Adding mentions to the queue.")
                """

                TODO: Add all of those mentions to the queue here.

                The "mentions" list contains a list of Status objects that
                need to be added to the queue. Keep in mind that if there
                are already objects in the queue, then we need to:

                1.) Make sure that the queue length does not exceed 20
                    Status objects.

                2.) Make sure that we keep track of which Status objects
                    are not being added onto the queue. We will need to
                    send a reply to those people stating that they could
                    not be added onto the queue.

                """


                #loops through the mentions list and add them to the queue
                #creates a list of items not added to the queue
                q = queue.Queue()
                for i in range(len(mentions)):
                    if(q.qsize > 20){
                        print("Sorry your request cannot be completed at this time")
                        not_added = mentions[i:len(mentions)]
                        break
                    }
                    else{
                        q.put(mentions[i])
                    }




            # Wait for one minute
            print("Enqueue Thread: Waiting.")
            time.sleep(20)

    # Dequeues a mention and executes the style transfer thread
    # If there are no mentions, then this will wait until there is a mention
    def __prune_queue(self, none):
        assert threading.current_thread().name == "dequeue_thread"

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
