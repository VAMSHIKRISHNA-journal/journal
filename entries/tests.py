from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User
from entries.models import Book, Entry, Profile
from django.urls import reverse

class EmailNotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        self.profile = self.user.profile
        self.profile.notify_email = 'friend@example.com'
        self.profile.save()
        self.book = Book.objects.create(user=self.user, title='Test Book')

    def test_email_sent_to_multiple_friends(self):
        self.client.login(username='testuser', password='password123')
        self.profile.notify_email = 'friend1@example.com, friend2@example.com'
        self.profile.save()
        
        url = reverse('entry-create', kwargs={'book_id': self.book.id})
        data = {
            'title': 'New Entry',
            'content': 'This is the content'
        }
        self.client.post(url, data)
        
        # We need to wait a tiny bit because of the thread, or just mock it.
        # But for this test, we can check mail.outbox if it eventually populates.
        # Actually, let's just wait a fraction of a second.
        import time
        time.sleep(0.5)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '📖 New Journal Entry: New Entry')
        self.assertIn('friend1@example.com', mail.outbox[0].to)
        self.assertIn('friend2@example.com', mail.outbox[0].to)
        self.assertEqual(len(mail.outbox[0].to), 2)
