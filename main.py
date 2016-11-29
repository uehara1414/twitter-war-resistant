import tweepy
import sqlite3
import os

DB_NAME = 'retweeted.db'


def get_uehara_api() -> tweepy.API:
    """メンションを監視する自分のアカウントの Tweepy API Object を返します

    :return: メンションを監視する自分のアカウントの Tweepy API Object
    """
    CONSUMER_KEY = os.environ["UEHARA_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["UEHARA_CONSUMER_SECRET"]

    ACCESS_TOKEN = os.environ["UEHARA_ACCESS_TOKEN"]
    ACCESS_SECRET = os.environ["UEHARA_ACCESS_SECRET"]

    return get_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


def get_tsugumi_api() -> tweepy.API:
    """引用リツイートをするアカウントの Tweepy API Object を返します

    :return: 引用リツイートをするアカウントの Tweepy API Object
    """
    CONSUMER_KEY = os.environ["TSUGUMI_CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["TSUGUMI_CONSUMER_SECRET"]

    ACCESS_TOKEN = os.environ["TSUGUMI_ACCESS_TOKEN"]
    ACCESS_SECRET = os.environ["TSUGUMI_ACCESS_SECRET"]

    return get_api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


def get_api(consumer_key: str, consumer_secret: str, access_token: str, access_secret: str):
    """API, ゲットだぜ！

    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return tweepy.API(auth)


def create_table_if_not_exists() -> None:
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS tweeteds
                              (tweet_id text PRIMARY KEY, author_screen_name text,content text, date text)''')
    conn.commit()


def is_already_retweeted_before(tweet_id: str) -> bool:
    create_table_if_not_exists()
    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()
    c.execute('SELECT * from tweeteds WHERE tweet_id=?', (tweet_id, ))
    if len(c.fetchall()) == 1:
        return True
    return False


def print_retweeted():
    create_table_if_not_exists()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for x in c.execute('SELECT * from tweeteds'):
        print(x)


def record_as_tweeted(tweet):
    create_table_if_not_exists()
    conn = sqlite3.connect(DB_NAME)

    c = conn.cursor()
    c.execute('INSERT INTO tweeteds VALUES(?, ?, ?, ?)', (tweet.id_str, tweet.author.screen_name, tweet.text, tweet.created_at))
    conn.commit()


def get_new_mention_with_VEP() -> list:
    api = get_uehara_api()
    l = api.mentions_timeline()

    targets = []
    for x in l:
        if 'VEP' in x.text.upper() and not is_already_retweeted_before(x.id_str):
            targets.append(x)
    return targets


def retweet_with_Python_is_good(display_name, tweet_id):
    api = get_tsugumi_api()
    content = construct_text_Python_is_good(display_name, tweet_id)
    api.update_status(content)


def construct_text_Python_is_good(display_name, tweet_id):
    content = "https://twitter.com/{}/status/{}".format(display_name, tweet_id)
    content += "\n@{} Pythonはいいぞ!".format(display_name)
    return content


def main():
    targets = get_new_mention_with_VEP()
    for x in targets:
        if __debug__:
            content = construct_text_Python_is_good(x.author.screen_name, x.id_str)
            print("dry retweet", content)
        else:
            retweet_with_Python_is_good(x.author.screen_name, x.id_str)
            record_as_tweeted(x)


if __name__ == '__main__':
    main()