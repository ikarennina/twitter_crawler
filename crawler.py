#!/usr/bin/env python
"""A basic Twitter crawler.

Given a user id, this module is capable of retrieving the following information:
    - User profile info
    - User tweets (if public)
    - User followers
    - User followees
"""
from collections import OrderedDict

import argparse
import json
import logging

import tweepy

class Crawler(object):
    """A basic twitter crawler."""

    def __init__(self, consumer_key, consumer_secret, access_token,
            access_token_secret):
        """Initialize crawler instance.

        Args:
            consumer_key: consumer_key as provided by twitter apps
            consumer_secret: consumer_secret as provided by twitter apps
            access_token: access_token as provided by twitter apps
            access_token_secret: access_token_secret as provided by twitter apps
            auth: authentication token
            api: tweepy api interface
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.auth = None
        self.api = None

    def connect(self):
        """Trigger authentication process."""
        self.auth = tweepy.OAuthHandler(self.consumer_key,
                    self.consumer_secret)
        self.auth.set_access_token(self.access_token,
                    self.access_token_secret)
        self.api = tweepy.API(self.auth)
        return self.api.verify_credentials()

    def get_user(self, user_id):
        """Return a User instance.

        Args:
            user_id: user id from Twitter
        """
        return User(user_id, self.api)

class User(object):
    """A class to provide all information about a user."""

    def __init__(self, user_id, api):
        """Initialize user.

        Args:
            user_id: user id from Twitter
            api: an authenticated instance of tweepy.API()
        """
        self.user_id = user_id
        self.api = api

    def get_profile_info(self, *args):
        """Get user profile information.

        The default information returned is:
         - id
         - screen_name
         - name
         - location
         - followers_count
         - status text

        Any arbitrary information provided by the Twitter API can also be
        retrieved by specifying it in *args.

        Args:
            *args: a variable-length list containing a keyword specifier for any
                additional information that should be included in the dictionary
                returned. This keyword should follow Twitter's API.

        Returns:
            info: a dictionary containing information about the user, indexed by
                strings representing an information specifier.

        Example:

        A call to get_profile_info('verified') to Dropbox user would return
        something like:

            {'followers_count': 3403626,
             'id': 14749606,
             'location': u'San Francisco, CA',
             'name': u'Dropbox',
             'screen_name': u'Dropbox',
             'status': u'We are excited to be expanding from 30 to over
                 200 in our Austin office. Come join us!
                 http://t.co/IIQxHRxAwx',
             'verified': True}
        """
        info = OrderedDict()
        user = self.api.get_user(self.user_id)
        info['id'] = user.id
        info['screen_name'] = user.screen_name
        info['name'] = user.name
        info['location'] = user.location
        info['followers_count'] = user.followers_count
        info['status'] = user.status.text
        for requested_info in args:
            if hasattr(user, requested_info):
                data = getattr(user, requested_info)
                info[requested_info] = data
            else:
                logging.warning('Requested attribute \'%s\' was not found in' +
                    ' user info and will be ignored.', requested_info)
        return info

    def get_followers(self, limit=100):
        """Get user's followers screen names.

        Args:
            limit: an optional argument that limits the number os results to be
                retrieved.
        """
        follower_cursor = tweepy.Cursor(self.api.followers, id=self.user_id)
        followers = []
        for user in follower_cursor.items(limit=limit):
            followers.append(user.screen_name)
        return followers

    def get_followees(self, limit=100):
        """Get user's followees screen names.

        Args:
            limit: an optional argument that limits the number os results to be
                retrieved.
        """
        followee_cursor = tweepy.Cursor(self.api.friends, id=self.user_id)
        followees = []
        for user in followee_cursor.items(limit=limit):
            followees.append(user.screen_name)
        return followees

    def get_tweets(self, limit=100):
        """Get user's tweets (starting from most recent).

        Args:
            limit: an optional argument that limits the number os results to be
                retrieved.
        """
        tweets_cursor = tweepy.Cursor(self.api.user_timeline, id=self.user_id)
        tweets = []
        for tweet in tweets_cursor.items(limit=limit):
            tweets.append(tweet.text)
        return tweets

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
    with open('auth.json') as json_data:
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
