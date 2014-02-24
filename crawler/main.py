import argparse
import json
import os

from crawler import Crawler

def print_info(user):
    """Print user info."""
    info = user.get_profile_info()
    print '----------  %s\'s profile info ----------' % info['name']
    for key, value in info.iteritems():
        print '%s: %s' % (key, value)
    print '----------  %s\'s followers ----------' % info['name']
    followers = user.get_followers()
    for follower in followers:
        print follower
    print '----------  %s\'s followees ----------' % info['name']
    followees = user.get_followees()
    for followee in followees:
        print followee
    print '----------  %s\'s tweets ----------' % info['name']
    tweets = user.get_tweets()
    for tweet in tweets:
        print tweet

def parse_command_line():
    """Parse command line arguments.

    Returns:
        user_id: The value provided via command line as the user identification.
    """
    parser = argparse.ArgumentParser(description='Crawl a twitter user ' +
            'information.')
    parser.add_argument('user_id',
            help='The or screen name of the user to be crawled.')
    args = parser.parse_args()
    return args.user_id

def main():
    """Main function."""
    package_directory = os.path.dirname(os.path.abspath(__file__))
    auth_file = os.path.join(package_directory, '../static', 'auth.json')
    with open(auth_file) as json_data:
        auth = json.load(json_data)
    crawler = Crawler(auth['consumer_key'],
                      auth['consumer_secret'],
                      auth['access_token'],
                      auth['access_token_secret']
                     )
    success = crawler.connect()
    if not success:
        logging.error('Could not authenticate. Program will terminate.')
        return
    user_id = parse_command_line()
    user = crawler.get_user(user_id)
    print_info(user)


if __name__ == '__main__':
    main()
