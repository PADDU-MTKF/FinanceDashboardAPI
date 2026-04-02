import uuid
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from .utils import generateToken

GOD_USER_USERNAME = "godadmin"
USER_KEY_PREFIX = "user:"
USERNAME_MAP = "username_map"  # username → uid
DATA_TIMEOUT = 3600  # 1 hour

TOKEN_PREFIX = "token:"
TOKEN_TIMEOUT = 1800  # 30 minutes


class User:
    VALID_ROLES = {"viewer", "analyst", "transactionAdmin","userAdmin","masterAdmin"}
    VALID_STATUS = {"active", "inactive"}

    def __init__(self, name, username, password, role="viewer", status="active", uid=None):
        if role not in self.VALID_ROLES:
            raise ValueError("Invalid role")

        if status not in self.VALID_STATUS:
            raise ValueError("Invalid status")

        if not username or not password:
            raise ValueError("Username and password required")

        self.uid = uid or str(uuid.uuid4())
        self.name = name
        self.username = username
        self.password = make_password(password)  # hash password
        self.role = role
        self.status = status

    # Password check
    def checkPassword(self, raw_password):
        return check_password(raw_password, self.password)

    # Role helpers
    def isTransactionAdmin(self):
        return self.role == "transactionAdmin"

    def isUserAdmin(self):
        return self.role == "userAdmin"

    def isMasterAdmin(self):
        return self.role == "masterAdmin"
    
    def isAnalyst(self):
        return self.role == "analyst"
    
    def isViewer(self):
        return self.role == "viewer"

    def is_active(self):
        return self.status == "active"

    # Update methods
    def updateRole(self, new_role):
        if new_role not in self.VALID_ROLES:
            raise ValueError("Invalid role")
        self.role = new_role

    def updateStatus(self, new_status):
        if new_status not in self.VALID_STATUS:
            raise ValueError("Invalid status")
        self.status = new_status

    # Serialization
    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        user = User(
            name=data["name"],
            username=data["username"],
            password=data["password"],  # already hashed
            role=data["role"],
            status=data["status"],
            uid=data["uid"]
        )
        user.password = data["password"]  # avoid re-hashing
        return user
    

class UserService:

    @staticmethod
    def _get_username_map():
        return cache.get(USERNAME_MAP, {})

    @staticmethod
    def _set_username_map(data):
        cache.set(USERNAME_MAP, data, timeout=DATA_TIMEOUT)

    @staticmethod
    def createUser(request_user: User, name, username, password, role="viewer"):
        if not request_user.isUserAdmin() and not request_user.isMasterAdmin():
            raise PermissionError("Only UserAdmin and MasterAdmin can create users")

        username_map = UserService._get_username_map()

        if username in username_map:
            raise ValueError("Username already exists")

        user = User(name, username, password, role)

        # store user
        cache.set(f"{USER_KEY_PREFIX}{user.uid}", user.to_dict(), timeout=DATA_TIMEOUT)

        # update username map
        username_map[username] = user.uid
        UserService._set_username_map(username_map)

        return user
    
    @staticmethod
    def createDefaultUser():
        username=GOD_USER_USERNAME
        password="godpassword"
        username_map = UserService._get_username_map()

        if username in username_map:
            raise ValueError("God admin already exists")

        user = User(name="God Admin", username=username, password=password, role="masterAdmin")

        # store user
        cache.set(f"{USER_KEY_PREFIX}{user.uid}", user.to_dict(), timeout=None)

        # update username map
        username_map[username] = user.uid
        UserService._set_username_map(username_map)

        return True

    @staticmethod
    def get_user_by_username(username):
        username_map = UserService._get_username_map()
        uid = username_map.get(username)

        if not uid:
            return None

        data = cache.get(f"{USER_KEY_PREFIX}{uid}")
        return User.from_dict(data) if data else None

    @staticmethod
    def login(username, password):
        user = UserService.get_user_by_username(username)

        if not user or not user.checkPassword(password):
            return None, None

        if not user.is_active():
            raise ValueError("User inactive")

        # generating token
        TOKEN = generateToken()
        cache.set(f"{TOKEN_PREFIX}{username}", TOKEN, timeout=TOKEN_TIMEOUT)

        return user, TOKEN

    @staticmethod
    def validateToken(username, token):
        cache_token = cache.get(f"{TOKEN_PREFIX}{username}")

        if not cache_token or cache_token != token:
            return None

        return UserService.get_user_by_username(username)
    
    @staticmethod
    def listAllUsers(request_user: User):
        # permission check
        if not request_user.isUserAdmin() and not request_user.isMasterAdmin():
            raise PermissionError("Only UserAdmin and MasterAdmin can view users")

        username_map = UserService._get_username_map()

        users = []

        for username, uid in username_map.items():
            data = cache.get(f"{USER_KEY_PREFIX}{uid}")

            if not data:
                continue

            user = User.from_dict(data)

            # hide password
            user_data = user.to_dict()
            user_data.pop("password", None)

            users.append(user_data)

        return users

    @staticmethod
    def updateUser(request_user: User, username, role=None, status=None):
        #base permission
        if not request_user.isUserAdmin() and not request_user.isMasterAdmin():
            raise PermissionError("Only UserAdmin and MasterAdmin can update users")

        username_map = UserService._get_username_map()
        uid = username_map.get(username)

        if not uid:
            raise ValueError("User not found")

        data = cache.get(f"{USER_KEY_PREFIX}{uid}")
        if not data:
            raise ValueError("User not found")

        user = User.from_dict(data)

        #protect god user role change
        if username.lower() == GOD_USER_USERNAME:
            raise PermissionError("God admin role cannot be changed")

        #userAdmin cannot modify masterAdmin
        if user.isMasterAdmin() and not request_user.isMasterAdmin():
            raise PermissionError("Only MasterAdmin can modify another MasterAdmin")

        # prevent self-demotion
        if request_user.username == username:
            raise PermissionError("User cannot update their own role or status")
        
        if role == "masterAdmin" and not request_user.isMasterAdmin():
            raise PermissionError("Only MasterAdmin can assign MasterAdmin role")

        # apply updates
        if role:
            user.updateRole(role)

        if status:
            user.updateStatus(status)

        cache.set(f"{USER_KEY_PREFIX}{uid}", user.to_dict(), timeout=DATA_TIMEOUT)

        return user

    @staticmethod
    def deleteUser(request_user: User, username):
        # role check
        if not request_user.isUserAdmin() and not request_user.isMasterAdmin():
            raise PermissionError("Only UserAdmin and MasterAdmin can delete users")

        # prevent deleting god user
        if username == GOD_USER_USERNAME:
            raise PermissionError("God admin cannot be deleted")

        username_map = UserService._get_username_map()
        uid = username_map.get(username)

        if not uid:
            raise ValueError("User not found")

        data = cache.get(f"{USER_KEY_PREFIX}{uid}")
        if not data:
            raise ValueError("User not found")

        # delete from cache
        cache.delete(f"{USER_KEY_PREFIX}{uid}")

        # remove from username map
        username_map.pop(username, None)
        UserService._set_username_map(username_map)

        return True
        