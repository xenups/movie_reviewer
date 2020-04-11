from rbac.acl import Registry
from rbac.context import IdentityContext
from rbac.proxy import RegistryProxy
from app_user.models import Message


class ACL(object):
    def __init__(self):
        self.acl = RegistryProxy(Registry())
        self.set_acl_rules()

    def set_acl_rules(self):
        self.acl.add_role("staff")
        self.acl.add_role("admin")
        self.acl.add_resource(Message)
        self.acl.allow("staff", "create", Message)
        self.acl.allow("admin", "edit", Message)

