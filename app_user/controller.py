"ICECREAM"
import bottle
from ICECREAM.cache import RedisCache
from ICECREAM.http import HTTPError
from ICECREAM.paginator import Paginate
from ICECREAM.rbac import ACLHandler
from ICECREAM.models.query import get_or_create
from app_user.models import User, Person, Message
from app_user.schemas import users_serializer, user_serializer


def get_users(db_session):
    try:
        page_number = bottle.request.GET.get('page') or 1
        page_size = bottle.request.GET.get('count') or 10
        users = db_session.query(User)
        return Paginate(users, int(page_number), int(page_size), users_serializer)

    except Exception as e:
        print(e)
        raise HTTPError(status=404, body="nemishe")


def hello():
    return {"id": "1", "name": "Thing1"}


def new_user(db_session, data):
    try:
        user_serializer.load(data)
    except Exception as e:
        raise HTTPError(404, e.args)

    cache = RedisCache()
    signup_token = cache.get_cache_multiple_value(data['phone'], 'signup_token')
    print(signup_token)
    if signup_token and signup_token == data["signup_token"]:
        person = data['person']
        person_name = person['name']
        person_last_name = person['last_name']
        person_bio = person['bio']
        phone = data['phone']
        person = get_or_create(Person, db_session, name=person_name)
        person.name = person_name
        person.last_name = person_last_name
        person.bio = person_bio
        db_session.add(person)
        user = get_or_create(User, db_session, phone=phone)
        user.phone = phone
        user.set_roles(data['roles'])
        user.set_password(data['password'])
        user.person = person
        db_session.add(user)
        db_session.commit()
        result = user_serializer.dump(db_session.query(User).get(user.id))
        return result
    raise HTTPError(404, "Signup Token Not Valid")


def new_message(db_session, data):
    user = bottle.request.get_user()
    current_user = db_session.query(User).get(user['id'])
    aclh = ACLHandler(Resource=Message)
    identity = aclh.get_identity(current_user)
    if identity.check_permission("create", Message):
        print("man staff am va mitunam add konam")
    if identity.check_permission("edit", Message):
        print("man admin am va mitunam edit konam")
    del aclh
