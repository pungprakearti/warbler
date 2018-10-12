"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, FollowersFollowee

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_app_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_list_users(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            # messages_add
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testuser', resp.data)

    def test_show_user(self):
        """Can we get the user's profile page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        user = User.query.filter(User.username == "testuser").one()

        resp = c.get(f"/users/{user.id}")

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'testuser', resp.data)

    def test_show_following(self):
        """Can we see who the user is following?"""

        c = self.client

        user = User.query.filter(User.username == "testuser").one()

        resp = c.get(f"/users/{user.id}/following")

        self.assertEqual(resp.status_code, 302)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f"/users/{user.id}/following")

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'followers">0</a>', resp.data)

    def test_show_followers(self):
        """Can we see the user's followers?"""

        c = self.client

        user = User.query.filter(User.username == "testuser").one()

        resp = c.get(f"/users/{user.id}/followers")

        self.assertEqual(resp.status_code, 302)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f"/users/{user.id}/followers")

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'following">0</a>', resp.data)

    def test_add_followers_logged_out(self):
        """Can we add followers while logged out?"""

        c = self.client

        f = User(
            id=2,
            email="testf@test.com",
            username="testuserf",
            password="HASHED_PASSWORD"
        )

        db.session.add(f)
        db.session.commit()

        resp = c.post("/users/follow/2")

        self.assertEqual(resp.status_code, 302)

    def test_add_followers_logged_in(self):
        """Can we add followers while logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        f = User(
            id=2,
            email="testf@test.com",
            username="testuserf",
            password="HASHED_PASSWORD"
        )

        db.session.add(f)
        db.session.commit()

        resp = c.post("/users/follow/2")

        self.assertEqual(resp.status_code, 302)

        ff = FollowersFollowee.query.filter(
            FollowersFollowee.follower_id == 2).one()

        self.assertEqual(ff.follower_id, 2)

    def test_stop_following_logged_out(self):
        """Can we unfollow while logged out?"""

        c = self.client

        f = User(
            id=2,
            email="testf@test.com",
            username="testuserf",
            password="HASHED_PASSWORD"
        )

        db.session.add(f)
        db.session.commit()

        resp = c.post("/users/stop-following/2")

        self.assertEqual(resp.status_code, 302)

    def test_stop_following_logged_in(self):
        """Can we stop following while logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        f = User(
            id=2,
            email="testf@test.com",
            username="testuserf",
            password="HASHED_PASSWORD"
        )

        db.session.add(f)
        db.session.commit()

        resp = c.post("/users/follow/2")

        new_resp = c.post("/users/stop-following/2")

        self.assertEqual(new_resp.status_code, 302)

        ff = FollowersFollowee.query.filter(
            FollowersFollowee.follower_id == 2).all()

        self.assertEqual(ff, [])

    def test_profile_logged_out(self):
        """Can we see the profile if we are logged out?"""

        c = self.client

        resp = c.get("/users/profile")

        self.assertEqual(resp.status_code, 302)

    def test_profile_logged_in(self):
        """Can we see the profile while logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get("/users/profile")

        self.assertIn(b"test@test.com", resp.data)

        # update user bio
        new_resp = c.post("/users/profile",
                          data={"bio": "hack the planet", "password": "testuser"})

        self.assertEqual(new_resp.status_code, 302)

        # get back to profile page with updated information
        resp = c.get("/users/profile")

        # check for updated information
        self.assertIn(b"hack the planet", resp.data)

    def test_delete_user_logged_out(self):
        """Can we delete the user while logged out?"""

        c = self.client

        resp = c.post("/users/delete")

        self.assertEqual(resp.status_code, 302)

    def test_delete_user_logged_in(self):
        """Can we delete the user while logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        # attempt to delete user
        resp = c.post("/users/delete")
        self.assertEqual(resp.status_code, 302)

        # check for any users in DB
        u = User.query.all()
        self.assertEqual(u, [])
