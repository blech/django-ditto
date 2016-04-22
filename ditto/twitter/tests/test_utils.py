# coding: utf-8
import json
from django.test import TestCase

from ..utils import htmlify_tweet


class UtilsHtmlifyTestCase(TestCase):

    # Define in child classes.
    api_fixture = None

    def getJson(self, filepath):
        json_file = open(filepath)
        json_data = json.loads(json_file.read())
        print(json_data)
        json_file.close()
        return json_data


class UtilsHtmlifyEntitiesTestCase(UtilsHtmlifyTestCase):
    "Linkify URLs from entities: urls, screen_names, hashtags."

    def test_links_urls(self):
        "Makes 'urls' entities into clickable links."
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_entities.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertTrue('with <a href="http://www.bbc.co.uk/news/business-34505593" rel="external">bbc.co.uk/news/business-…</a>' in tweet_html)
        self.assertTrue('and <a href="http://www.wired.com/2015/10/meet-walking-dead-hp-cisco-dell-emc-ibm-oracle/" rel="external">wired.com/2015/10/meet-w…</a>' in tweet_html)

    def test_links_users(self):
        "Makes 'user_mentions' entities into clickable @links."
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_entities.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertTrue('for <a href="https://twitter.com/philgyford" rel="external">@philgyford</a>' in tweet_html)
        self.assertTrue('and <a href="https://twitter.com/samuelpepys" rel="external">@samuelpepys</a>' in tweet_html)

    def test_links_users_with_entities(self):
        "It was trying to run urlize() on the tweet after linking the user mention."
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_users_no_urls.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertEqual('<a href="https://twitter.com/genmon" rel="external">@genmon</a> lovely, on my way.', tweet_html)

    def test_links_hashtags(self):
        "Makes 'hashtags' entities into clickable #links."
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_entities.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertTrue(' <a href="https://twitter.com/search?q=%23testing" rel="external">#testing</a> and' in tweet_html)
        self.assertTrue(' <a href="https://twitter.com/search?q=%23hashtag" rel="external">#hashtag</a>' in tweet_html)

    def test_links_substringed_hashtags(self):
        "If a hashtag is a substring of another, it should cope OK."
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_substringed_hashtags.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertTrue('@denisewilton</a> <a href="https://twitter.com/search?q=%23LOVEWHATYOUDO" rel="external">#LOVEWHATYOUDO</a> <a href="https://twitter.com/search?q=%23DOWHATYOULOVE" rel="external">#DOWHATYOULOVE</a>' in tweet_html)

    def test_links_symbols(self):
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_symbols.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertEqual(tweet_html,
            'Some symbols: <a href="https://twitter.com/search?q=%24AAPL" rel="external">$AAPL</a> and <a href="https://twitter.com/search?q=%24PEP" rel="external">$PEP</a> and $ANOTHER and <a href="https://twitter.com/search?q=%24A" rel="external">$A</a>.'
        )

class UtilsHtmlifyFormattingTestCase(UtilsHtmlifyTestCase):

    api_fixture = 'ditto/twitter/fixtures/api/tweet_with_entities.json'

    def setUp(self):
        self.json_data = self.getJson(self.api_fixture)

    def test_linebreaks(self):
        "Turns linebreaks into <br>s"
        tweet_html = htmlify_tweet(self.json_data)
        self.assertTrue("""A<br>test for""" in tweet_html)

    def test_strip(self):
        "Strips whitespace at start and end"
        tweet = self.json_data
        tweet['text'] = ' X' + tweet['text'] + 'Y '
        tweet_html = htmlify_tweet(tweet)
        self.assertEqual('X', tweet_html[0])
        self.assertEqual('Y', tweet_html[-1])


class UtilsHtmlifyUrlsTestCase(UtilsHtmlifyTestCase):
    "Further tests for specific problems with URLs."

    def test_urls_in_archived_tweets(self):
        """Old Tweets included in the downloaded archive files don't have
        'entities' elements, so we need to manually link any URLs in their
        tweets.
        """
        api_fixture = 'ditto/twitter/fixtures/api/tweet_from_archive_2006.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertEqual(tweet_html,
            'Made a little Twitter thing: <a href="http://www.gyford.com/phil/writing/2006/12/02/quick_twitter.php">http://www.gyford.com/phil/writing/2006/12/02/quick_twitter.php</a>')

    def test_urls_with_no_media(self):
        """The 'entities' element has no 'media'."""
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_entities_2.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertTrue('created. <a href="http://daveaddey.com/postfiles/ecoatm.jpg" rel="external">daveaddey.com/postfiles/ecoa…</a>' in tweet_html)

    def test_urls_containing_user_mentions(self):
        """A full URL that contains a user_mention. Which means we should parse
        user_mentions before adding the full URLs.
        """
        api_fixture = 'ditto/twitter/fixtures/api/tweet_with_entities_3.json'
        tweet_html = htmlify_tweet( self.getJson(api_fixture) )
        self.assertTrue('prototyping!  <a href="https://medium.com/@BuckleyWilliams/hello-from-buckley-williams-announcing-our-new-studio-c48e20c847d0" rel="external">medium.com/@BuckleyWillia…</a>' in tweet_html)


class UtilsHtmlifyPhotosTestCase(UtilsHtmlifyTestCase):
    "Remove links to photos in the tweet text."

    api_fixture = 'ditto/twitter/fixtures/api/tweet_with_photos.json'

    def setUp(self):
        self.json_data = self.getJson(self.api_fixture)

    def test_removes_photo_links(self):
        tweet_html = htmlify_tweet(self.json_data)
        self.assertEqual('Testing multiple images.', tweet_html)

