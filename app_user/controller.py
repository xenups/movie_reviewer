"ICECREAM"
import bottle
from marshmallow import ValidationError
from app_user.models import User, Person
from bottle import HTTPResponse, HTTPError
from ICECREAM.models.query import get_or_create
from app_user.schemas import user_serializer, users_serializer


def get_users(db_session):
    user = bottle.request.get_user()
    print(user)
    try:
        users = db_session.query(User).all()
        users = users_serializer.dump(users)
        return users

    except Exception:
        raise HTTPError(status=404, body="nemishe")


def new_user(db_session, data):
    try:
        try:
            user_serializer.load(data)

            person = data['person']
            person_name = person['name']
            person_last_name = person['last_name']
            person_phone = person['phone']
            person_bio = person['bio']
            username = data['username']
            person = get_or_create(Person, db_session, name=person_name)
            person.name = person_name
            person.last_name = person_last_name
            person.phone = person_phone
            person.bio = person_bio
            db_session.add(person)
            user = get_or_create(User, db_session, username=username)
            user.username = username
            user.set_password(data['password'])
            user.person = person
            db_session.add(user)
            db_session.commit()
            result = user_serializer.dump(db_session.query(User).get(user.id))
            return result
        except ValidationError as err:
            return err.messages
    except HTTPError as err:
        raise HTTPError(status=404, body="something")
