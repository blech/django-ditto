from django.core.urlresolvers import reverse
from django.test import TestCase

from .. import factories


class TwitterViewTests(TestCase):

    def test_home_templates(self):
        "The Twitter home page uses the correct templates"
        response = self.client.get(reverse('twitter:index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'twitter/index.html')
        self.assertTemplateUsed(response, 'twitter/base.html')
        self.assertTemplateUsed(response, 'ditto/base.html')

    def test_home_context(self):
        "The Twitter home page sends the correct data to templates"
        accounts = factories.AccountFactory.create_batch(3)
        tweets_1 = factories.TweetFactory.create_batch(
                                                    5, user=accounts[0].user)
        tweets_2 = factories.TweetFactory.create_batch(
                                                    5, user=accounts[1].user)
        response = self.client.get(reverse('twitter:index'))
        self.assertIn('account_list', response.context)
        self.assertIn('tweet_list', response.context)
        # Three accounts, only two of which have Tweets:
        self.assertEqual(
            [account.pk for account in response.context['account_list']],
            [1,2,3]
        )
        # Tweets for both accounts that have them:
        self.assertEqual(
            [tweet.pk for tweet in response.context['tweet_list']],
            [10,9,8,7,6,5,4,3,2,1]
        )

    def test_home_privacy(self):
        """Only public Tweets should appear."""
        private_user = factories.UserFactory(is_private=True)
        public_user = factories.UserFactory(is_private=False)

        # We only display tweets from Accounts, so add some.
        private_account = factories.AccountFactory(user=private_user)
        public_account = factories.AccountFactory(user=public_user)

        public_tweet_1 = factories.TweetFactory(user=public_user)
        private_tweet = factories.TweetFactory(user=private_user)
        public_tweet_2 = factories.TweetFactory(user=public_user)

        response = self.client.get(reverse('twitter:index'))
        tweets = response.context['tweet_list']
        self.assertEqual(len(tweets), 2)
        self.assertEqual(tweets[0].pk, public_tweet_2.pk)
        self.assertEqual(tweets[1].pk, public_tweet_1.pk)

    def test_account_detail_templates(self):
        "Uses the correct templates"
        account = factories.AccountFactory.create()
        response = self.client.get(reverse('twitter:account_detail',
                            kwargs={'screen_name': account.user.screen_name}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'twitter/account_detail.html')
        self.assertTemplateUsed(response, 'twitter/base.html')
        self.assertTemplateUsed(response, 'ditto/base.html')

    def test_account_detail_context(self):
        "Sends the correct data to templates"
        account_1 = factories.AccountFactory.create()
        account_2 = factories.AccountFactory.create()
        tweets_1 = factories.TweetFactory.create_batch(3, user=account_1.user)
        tweets_2 = factories.TweetFactory.create_batch(3, user=account_2.user)
        response = self.client.get(reverse('twitter:account_detail',
                        kwargs={'screen_name': account_1.user.screen_name}))
        self.assertIn('account', response.context)
        self.assertEqual(account_1.pk, response.context['account'].pk)
        self.assertIn('tweet_list', response.context)
        self.assertEqual(len(response.context['tweet_list']), 3)
        self.assertEqual(
            [twitter.pk for twitter in response.context['tweet_list']],
            [3,2,1]
        )

    def test_account_detail_privacy(self):
        "It does not show private Tweets"
        user = factories.UserFactory.create(is_private=True)
        account = factories.AccountFactory.create(user=user)
        tweets_1 = factories.TweetFactory.create_batch(3, user=user)
        response = self.client.get(reverse('twitter:account_detail',
                                    kwargs={'screen_name': user.screen_name}))
        self.assertIn('account', response.context)
        self.assertEqual(len(response.context['tweet_list']), 0)

