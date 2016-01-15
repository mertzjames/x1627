"""
[x1627]()
"""

import time
import praw
import random
import pykcd
import logging

from requests import HTTPError
from helper import user, password

words_to_monitor = ['fake', 'no way']
what_to_say = [
    'woosh', 'Comment of the year', 'Are you for real',
    "I'm taking a screenshot so I can remember this moment forever"
]
two_days = 172800

comment_responses = {}
cur_comic_processed = 1
last_updated = None


def update_comment_responses():
    global comment_responses
    global cur_comic_processed
    global last_updated

    print("Updating comment responses....")

    finished_processing = False
    while not finished_processing:
        try:
            print("Processing comic # {}".format(cur_comic_processed))
            strip = pykcd.XKCDStrip(cur_comic_processed)
            comment_responses[strip.title.lower()] = strip.alt_text
            cur_comic_processed += 1
        except HTTPError as e:
            if '404' in str(e):
                finished_processing = True
            else:
                raise e

        except ValueError as e:
            print(e)
            print("Skipping comic {}".format(cur_comic_processed))
            cur_comic_processed += 1

    last_updated = time.time()


def bot_reply(r: praw.Reddit, comment: praw.objects.Comment):
    global comment_responses
    print("Addressing comment w/ id: {}".format(comment.id))
    potential_responses = [k[1] for k in comment_responses.items() if k[0] in comment.body.lower()]
    if len(potential_responses) > 0:
        response = random.choice(potential_responses)
        comment.reply(response)

    comment.mark_as_read()
    time.sleep(random.randint(5, 15))  # randomly wait 5 - 15 seconds to make it seem like we're "typing"


def whoosh(r: praw.Reddit):
    print("Looking for unsuspecting victim")
    comment_made = False
    while not comment_made:

        random_sub = r.get_random_subreddit()

        print("Searching top submissions of {}".format(random_sub.display_name))

        try:
            for submission in random_sub.get_hot(limit=10):

                flat_comments = praw.helpers.flatten_tree(submission.comments)
                for comment in flat_comments:
                    if any(string in comment.body for string in words_to_monitor):
                        print("Victim Found!")
                        comment.reply(random.choice(what_to_say))
                        print("Comment made to post {} with comment id {}".format(submission.id, comment.id))
                        comment_made = True
                        break  # Only antagonize our first found victim.  Nothing more.
                else:
                    continue
                break

            else:
                continue
            break

        except (AttributeError, praw.errors.APIException) as e:
            print("Error encountered:")
            print(e)
            print("Moving onto next sub")


def main():
    r = praw.Reddit(user_agent='x1627')

    print("Logging in....")
    r.login(user, password, disable_warning=True)
    print("Success!")
    already_done = set()
    time_to_wait = 0
    then = time.time()
    update_comment_responses()

    # main loop
    while True:

        now = time.time()

        if now - then > time_to_wait:
            whoosh(r)
            time_to_wait = random.randint(900, 10800)  # 15 minutes to 3 hours
            print("Time to wait for next victim: {} seconds".format(time_to_wait))

        # get "unread" responses and address them
        for item in r.get_unread():
            bot_reply(r, item)

        # check to see if it's time to update responses:
        if now - last_updated > two_days:
            update_comment_responses()

        time.sleep(30)  # check for responses every 30 seconds

if __name__ == '__main__':

    main()
