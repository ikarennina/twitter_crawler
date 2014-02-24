import argparse
import json
import os

from crawler import Crawler

def print_info(user):
    """Print user info."""
    info = user.get_profile_info()
    print '\n----------  %s\'s profile info ----------\n' % info['name']
    for key, value in info.iteritems():
        print '%s: %s' % (key, value)

    print '\n----------  %s\'s followers ----------\n' % info['name']
    followers = user.get_followers()
    if not followers:
        print 'Account is private and followers cannot be crawled.'
    else:
        for follower in followers:
            print follower

    print '\n----------  %s\'s followees ----------\n' % info['name']
    followees = user.get_followees()
    if not followees:
        print ('Account is private and followed accounts cannot be' +
            ' crawled.')
    else:
        for followee in followees:
            print followee

    print '\n----------  %s\'s tweets ----------\n' % info['name']
    tweets = user.get_tweets()
    if not followers:
        print 'Account is private and tweets cannot be crawled.'
    else:
        for tweet in tweets:
            print tweet
    print ''

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
