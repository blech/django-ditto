# coding: utf-8
from mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.six import StringIO

from .. import factories


class FetchTwitterTweetsArgs(TestCase):

    def test_fail_with_no_args(self):
        "Fails when no arguments are provided"
        with self.assertRaises(CommandError):
            call_command('fetch_twitter_tweets')

    def test_fail_with_account_only(self):
        "Fails when only an account is provided"
        with self.assertRaises(CommandError):
            call_command('fetch_twitter_tweets', account='terry')

    @patch('ditto.twitter.management.commands.fetch_twitter_tweets.RecentTweetsFetcher')
    def test_with_recent(self, fetch_class):
        "Calls the correct method when fetching recent tweets"
        call_command('fetch_twitter_tweets', '--recent', stdout=StringIO())
        fetch_class.assert_called_once_with(screen_name=None)

    @patch('ditto.twitter.management.commands.fetch_twitter_tweets.RecentTweetsFetcher')
    def test_with_recent_and_account(self, fetch_class):
        "Calls the correct method when fetching one account's recent tweets"
        call_command('fetch_twitter_tweets', '--recent', account='barbara',
                                                            stdout=StringIO())
        fetch_class.assert_called_once_with(screen_name='barbara')

    @patch('ditto.twitter.management.commands.fetch_twitter_tweets.FavoriteTweetsFetcher')
    def test_with_favorites(self, fetch_class):
        "Calls the correct method when fetching favorite tweets"
        call_command('fetch_twitter_tweets', '--favorites', stdout=StringIO())
        fetch_class.assert_called_once_with(screen_name=None)

    @patch('ditto.twitter.management.commands.fetch_twitter_tweets.FavoriteTweetsFetcher')
    def test_with_favorites_and_account(self, fetch_class):
        "Calls the correct method when fetching one account's favorite tweets"
        call_command('fetch_twitter_tweets', '--favorites',
                                    account='barbara', stdout=StringIO())
        fetch_class.assert_called_once_with(screen_name='barbara')


class FetchTwitterTweetsOutput(TestCase):

    @patch('ditto.twitter.management.commands.fetch_twitter_tweets.RecentTweetsFetcher.fetch')
    def test_success_output(self, fetch_method):
        "Responds correctly when recent tweets were successfully fetched"
        # What the mocked method will return:
        fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': True, 'fetched': 23}]
        ]
        out = StringIO()
        call_command('fetch_twitter_tweets', '--recent', stdout=out)
        self.assertIn('philgyford: Fetched 23 tweets', out.getvalue())

    @patch('ditto.twitter.management.commands.fetch_twitter_tweets.RecentTweetsFetcher.fetch')
    def test_error_output(self, fetch_method):
        "Responds correctly when there was an error fetching recent tweets"
        # What the mocked method will return:
        fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': False, 'message': 'It broke'}]
        ]
        out = StringIO()
        out_err = StringIO()
        call_command('fetch_twitter_tweets', '--recent', stdout=out,
                                                                stderr=out_err)
        self.assertIn('philgyford: Failed to fetch tweets: It broke',
                                                            out_err.getvalue())


class FetchAccounts(TestCase):

    @patch('ditto.twitter.management.commands.fetch_accounts.VerifyFetcher.fetch')
    def test_success_output(self, fetch_method):
        "Responds correctly when users were successfully fetched"
        # What the mocked method will return:
        fetch_method.side_effect = [
            [{'account': 'philgyford', 'success': True}]
        ]
        out = StringIO()
        call_command('fetch_accounts', stdout=out)
        self.assertIn('Fetched @philgyford', out.getvalue())

    @patch('ditto.twitter.management.commands.fetch_accounts.VerifyFetcher.fetch')
    def test_error_output(self, fetch_method):
        "Responds correctly when there was an error fetching useres"
        # What the mocked method will return:
        fetch_method.side_effect = [
                [{'account': 'philgyford', 'success': False,
                    'message': 'It broke'}]
        ]
        out = StringIO()
        out_err = StringIO()
        call_command('fetch_accounts', stdout=out, stderr=out_err)
        self.assertIn('Could not fetch @philgyford: It broke',
                                                            out_err.getvalue())


class ImportTweets(TestCase):

    def test_fails_with_no_args(self):
        "Fails when no arguments are provided"
        with self.assertRaises(CommandError):
            call_command('import_tweets')

    def test_fails_with_invalid_directory(self):
        with patch('os.path.isdir', return_value=False):
            with self.assertRaises(CommandError):
                call_command('import_tweets', path='/wrong/path')

    @patch('ditto.twitter.management.commands.import_tweets.TweetIngester.ingest')
    def test_calls_ingest_method(self, ingest_mock):
        out = StringIO()
        with patch('os.path.isdir', return_value=True):
            call_command('import_tweets', path='/right/path', stdout=out)
            ingest_mock.assert_called_once_with(
                                        directory='/right/path/data/js/tweets')

    @patch('ditto.twitter.management.commands.import_tweets.TweetIngester.ingest')
    def test_success_output(self, ingest_mock):
        """Outputs the correct response if ingesting succeeds."""
        ingest_mock.return_value = {
            'success': True, 'tweets': 12345, 'files': 21
        }
        out = StringIO()
        with patch('os.path.isdir', return_value=True):
            call_command('import_tweets', path='/right/path', stdout=out)
            self.assertIn('Imported 12345 tweets from 21 files', out.getvalue())

    @patch('ditto.twitter.management.commands.import_tweets.TweetIngester.ingest')
    def test_error_output(self, ingest_mock):
        """Outputs the correct error if ingesting fails."""
        ingest_mock.return_value = {
            'success': False, 'message': 'Something went wrong',
        }
        out = StringIO()
        out_err = StringIO()
        with patch('os.path.isdir', return_value=True):
            call_command('import_tweets', path='/right/path',
                                                    stdout=out, stderr=out_err)
            self.assertIn('Something went wrong', out_err.getvalue())

