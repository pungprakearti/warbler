"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, FollowersFollowee


db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(FollowersFollowee, DictReader(follows))


# testAccount to seed for testing
testAccount = User.signup(
    username='testAccount',
    email='test@test.com',
    password='test12',
    image_url='https://amp.businessinsider.com/images/5899ffcf6e09a897008b5c04-750-750.jpg',
)
# Added a bio and location
testAccount.bio = 'Bio for testAccount so good'
testAccount.location = 'San Francisco, CA'
# add account to db
db.session.add(testAccount)

db.session.commit()
