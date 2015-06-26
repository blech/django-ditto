from django.db import IntegrityError
from django.test import TestCase

from .. import factories
from ..models import Bookmark


class PinboardAccountTests(TestCase):

    def test_str(self):
        account = factories.AccountFactory(username='bill')
        self.assertEqual(account.__str__(), 'Pinboard: bill')

    def test_service_name(self):
        account = factories.AccountFactory()
        self.assertEqual(account.service_name, 'Pinboard')

class PinboardBookmarkTests(TestCase):

    def test_save(self):
        "Make sure its save() method calls the parent, so actually saves."
        bookmark = factories.BookmarkFactory(title='My title')
        bookmark.save()
        b = Bookmark.objects.get(title='My title')
        self.assertEqual(b.pk, bookmark.pk)

    def test_url_constraint(self):
        """url must be unique for an Account's Bookmarks"""
        account = factories.AccountFactory()
        bookmark_1 = factories.BookmarkFactory(
                                account=account, url='http://www.example.com')
        bookmark_1.save()
        with self.assertRaises(IntegrityError):
            bookmark_2 = factories.BookmarkFactory(
                                account=account, url='http://www.example.com')

    def test_url_unconstrained(self):
        """URLs do not have to be unique for different Accounts' Bookmarks"""
        account_1 = factories.AccountFactory()
        bookmark_1 = factories.BookmarkFactory(
                            account=account_1, url='http://www.example.com')
        bookmark_1.save()
        account_2 = factories.AccountFactory()
        try:
            bookmark_2 = factories.BookmarkFactory(
                            account=account_2, url='http://www.example.com')
        except IntegrityError:
            self.fail("It looks like there's a Unique constraint on Bookmark.url, which there shouldn't be.")

    def test_summary_creation(self):
        "Make sure it creates Item's summary."
        bookmark = factories.BookmarkFactory(description='My description')
        self.assertEqual(bookmark.summary, bookmark.description)

    def test_get_absolute_url(self):
        bookmark = factories.BookmarkFactory()
        self.assertEqual(bookmark.get_absolute_url(), '/pinboard/1')


