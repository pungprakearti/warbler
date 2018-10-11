"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, FollowersFollowee

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_app_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        FollowersFollowee.query.delete()

        db.session.commit()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(u.messages.count(), 0)
        self.assertEqual(u.followers.count(), 0)
        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.username, "testuser")
        self.assertEqual(u.password, 'HASHED_PASSWORD')
        self.assertEqual(u.image_url, "/static/images/default-pic.png")
        self.assertEqual(u.header_image_url, "/static/images/warbler-hero.jpg")

    def test_repr(self):
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        u = User.query.get(1)

        repr_return = u.__repr__()

        self.assertEqual(repr_return, '<User #1: testuser, test@test.com>')
        self.assertNotEqual(repr_return, '<Userasdfsdfdsfdsm>')

    def test_follows(self):
        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        f = User(
            id=2,
            email="testf@test.com",
            username="testuserf",
            password="HASHED_PASSWORD"
        )

        ff = FollowersFollowee(
            follower_id=1,
            followee_id=2
        )

        db.session.add(u)
        db.session.add(f)

        db.session.commit()

        db.session.add(ff)

        db.session.commit()

        self.assertEqual(u.is_followed_by(f), True)
        self.assertEqual(f.is_followed_by(u), False)

        self.assertEqual(u.is_following(f), False)
        self.assertEqual(f.is_following(u), True)

    def test_signup(self):
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url="image_url"
        )

        db.session.commit()

        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.username, "testuser")
        self.assertEqual(u.image_url, "image_url")
        self.assertIs(bcrypt.check_password_hash(
            u.password, "HASHED_PASSWORD"), True)
        self.assertIs(bcrypt.check_password_hash(
            u.password, "NOT_HASHED_PASSWORD"), False)
        self.assertEqual(User.authenticate(u.username, "HASHED_PASSWORD"), u)
        self.assertIs(User.authenticate(
            u.username, "NOT_HASHED_PASSWORD"), False)
