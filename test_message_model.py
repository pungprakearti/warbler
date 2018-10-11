from app import app
from models import db, Message, User, Like
import datetime
import unittest

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_app_test'
db.create_all()


class ApplicationTest(unittest.TestCase):

    def setUp(self):
        """Set up our test client and make a new cupcake for each test to work with"""
        self.client = app.test_client()
        new_message = Message(
            id=1,
            text="Testing",
            timestamp=datetime.datetime(2018, 1, 1, 1, 1, 1, 1),
            user_id=1
        )

        new_user = User(
            id=1,
            email='test@test.com',
            username='TestUser',
            image_url='/static/images/default-pic.png',
            header_image_url='/static/images/warbler-hero.jpg',
            bio='Test Bio',
            location='Test Location',
            password='password'
        )

        new_like = Like(
            user_id=1,
            message_id=1
        )

        db.session.add(new_message)
        db.session.add(new_user)
        db.session.add(new_like)

        db.session.commit()

    def tearDown(self):
        """Delete all the cupcakes from the db after each test to start with clean data"""

        Message.query.delete()
        User.query.delete()
        Like.query.delete()
        db.session.commit()

    def test_attribute(self):
        message = Message.query.get(1)

        self.assertEqual(message.text, 'Testing')
        self.assertEqual(message.user_id, 1)
        self.assertEqual(message.timestamp, datetime.datetime(
            2018, 1, 1, 1, 1, 1, 1))
        self.assertNotEqual(message.text, 'asdf')
        self.assertNotEqual(message.user_id, 'asdf')
        self.assertNotEqual(message.timestamp, 'asdf')

    def test_is_liked_by(self):
        message = Message.query.get(1)
        user = User.query.get(1)
        like = Like.query.get((1, 1))

        wrong_user = User(
            id=7,
            email='test7@test.com',
            username='TestUser7',
            image_url='/static/images/default-pic.png',
            header_image_url='/static/images/warbler-hero.jpg',
            bio='Test Bio',
            location='Test Location',
            password='password'
        )

        db.session.add(wrong_user)
        db.session.commit()

        message = Message.is_liked_by(user, message)
        wrong_message = Message.is_liked_by(wrong_user, message)

        self.assertEqual(message, like)
        self.assertEqual(wrong_message, None)
