"ICECREAM"
import bottle
from marshmallow import ValidationError
from app_user.models import User, Person, Message
from bottle import HTTPResponse, HTTPError
from ICECREAM.models.query import get_or_create
from app_user.schemas import user_serializer, users_serializer
from rbac.acl import Registry
from rbac.proxy import RegistryProxy
from rbac.context import IdentityContext, PermissionDenied


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
            user.set_roles(data['roles'])
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


def new_message(db_session, data):
    user = bottle.request.get_user()
    acl = RegistryProxy(Registry())
    current_user = db_session.query(User).get(user['id'])
    identity = IdentityContext(acl, lambda: current_user.get_roles())
    acl.add_role("staff")
    acl.add_role("admin")
    acl.add_resource(Message)

    acl.allow("staff", "create", Message)

    message = Message(content="slm manam", owner=current_user)

    with identity.check_permission("create", Message):
        print("ejaze dara")
