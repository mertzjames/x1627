import time
import praw
import random

def main():
    r = praw.Reddit(user_agent='x1627')

    print("Logging in....")
    r.login('username', 'password', disable_warning=True)
    print("Success!")
    already_done = set()

    words_to_monitor = ['fake', 'no way']
    what_to_say = [
        'woosh', 'Comment of the year', 'Are you for real',
        "I'm taking a screenshot so I can remember this moment forever"
    ]

    while True:

        print("Looking for unsuspecting victim")
        comment_made = False

        while not comment_made:

            random_sub = r.get_random_subreddit()

            print("Searching top submissions of {}".format(random_sub.display_name))
            for submission in random_sub.get_hot(limit=10):

                flat_comments = praw.helpers.flatten_tree(submission.comments)
                for comment in flat_comments:
                    if any(string in comment.body for string in words_to_monitor):
                        print("Victim Found!")
                        comment.reply(random.choice(what_to_say))
                        print("Comment made to post {} with comment id {}".format(submission.id, comment.id))
                        comment_made = True

        time.sleep(random.randint(1800, 259200))  # 30 minutes to 3 days


if __name__ == '__main__':

    main()
