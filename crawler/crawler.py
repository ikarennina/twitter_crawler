#!/usr/bin/env python
"""A basic Twitter crawler.

Given a user id, this module is capable of retrieving the following information:
    - User profile info
    - User tweets (if public)
    - User followers
    - User followees
"""
from collections import OrderedDict

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
    """A class to provide all information about a user.
    
    Attributes:
        user_id: user unique identifier on Twitter
        user: an object carrying user info
        api: tweepy authenticated API object
        protected: a boolean indicating if the account is either protected or
            public
    """

    def __init__(self, user_id, api):
        """Initialize user.

        Args:
            user_id: user id from Twitter
            api: an authenticated instance of tweepy.API()
        """
        self.user_id = user_id
        self.user = api.get_user(user_id)
        self.api = api
        self.protected = self.user.protected

    def get_profile_info(self, *args):
        """Get user profile information.

        The default information returned is:
         - id
         - screen_name
         - name
         - location
         - followers_count
         - status text (if account is public)

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
        info['id'] = self.user.id
        info['screen_name'] = self.user.screen_name
        info['name'] = self.user.name
        info['location'] = self.user.location
        info['followers_count'] = self.user.followers_count
        if not self.protected:
            info['status'] = self.user.status.text
        for requested_info in args:
            if hasattr(self.user, requested_info):
                data = getattr(self.user, requested_info)
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

        Returns:
            followers: a list of the screen names of the user followers.
            None: if the account is protected and no follower can be crawled.
        """
        if self.protected:
            return None
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

        Returns:
            followees: a list of the screen names of acconts that the user
                follows.
            None: if the account is protected and no account followed can be crawled.
        """
        if self.protected:
            return None
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

        Returns:
            tweets: a list of te text of every tweet, up to 'limit' tweets.
            None: if the account is protected and no tweet can be crawled.
        """
        if self.protected:
            return None
        tweets_cursor = tweepy.Cursor(self.api.user_timeline, id=self.user_id)
        tweets = []
        for tweet in tweets_cursor.items(limit=limit):
            tweets.append(tweet.text)
        return tweets

