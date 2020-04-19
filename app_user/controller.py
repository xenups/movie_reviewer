"ICECREAM"
import bottle
from ICECREAM.http import HTTPError, HTTPResponse
from ICECREAM.paginator import Paginate
from ICECREAM.rbac import get_user_identity
from ICECREAM.models.query import get_or_create, get_object, is_object_exist_409, get_object_or_404
from app_user.models import User, Person, Message
from app_user.schemas import users_serializer, user_serializer


def hello():
    return {"id": "1", "name": "Thing1"}


def get_users(db_session):
    try:
        page_number = bottle.request.GET.get('page') or 1
        page_size = bottle.request.GET.get('count') or 10
        users = db_session.query(User)
        return Paginate(users, int(page_number), int(page_size), users_serializer)
    except Exception as e:
        raise HTTPError(status=404, body="Something wrong")


def get_user(pk, db_session):
    user = get_object_or_404(User, db_session, User.id == pk)
    result = user_serializer.dump(user)
    raise HTTPResponse(status=200, body=result)


def delete_user(pk, db_session):
    identity = get_user_identity(db_session)
    if identity.check_permission("delete_user", User):
        user = get_object_or_404(User, db_session, User.id == pk)
        db_session.delete(user)
        db_session.commit()
        raise HTTPResponse(status=204, body="Successfully deleted !")
    raise HTTPError(status=403, body="Access denied")


def create_user(db_session, data):
    try:
        user_serializer.load(data)
    except Exception as e:
        raise HTTPError(404, e.args)
    identity = get_user_identity(db_session)
    if identity.check_permission("add_user", User):
        is_object_exist_409(User, db_session, User.phone == data['phone'])
        person = data['person']
        person_obj = get_or_create(Person, db_session, name=person['name'])
        person_obj.name = person['name']
        person_obj.last_name = person['last_name']
        person_obj.bio = person['bio']
        db_session.add(person_obj)
        user = get_or_create(User, db_session, phone=data['phone'])
        user.phone = data['phone']
        user.set_roles(data['roles'])
        user.set_password(data['password'])
        user.person = person_obj
        db_session.add(user)
        db_session.commit()
        result = user_serializer.dump(db_session.query(User).get(user.id))
        return result
    raise HTTPError(403, "Access denied")
