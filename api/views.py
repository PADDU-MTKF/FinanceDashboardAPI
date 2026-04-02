from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.parsers import MultiPartParser, FormParser

from .modules.userClass import User,UserService


#default user creation
try:
    UserService.createDefaultUser()
except:
    pass


# HELPER FUNCTIONS ***********************************************************************************

def api_response(success, code, message, data=None, errors=None):
    return Response(
        {
            "success": success,
            "code": code,
            "message": message,
            "data": data,
            "errors": errors
        },
        status=code
    )

def get_request_user(request):
    token = request.headers.get("TOKEN")
    username = request.headers.get("USERNAME")

    if not token or not username:
        return None

    return UserService.validateToken(username, token)


# VIEWS ************************************************************************************************

@api_view(['GET'])
def home(request):
    return api_response(
        True,
        status.HTTP_200_OK,
        "API is working",
        data={"status": "ok"}
    )


class LoginAPI(APIView):

    def post(self, request):
        try:
            username = request.data["username"]
            password = request.data["password"]
        except KeyError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Missing required fields",
                errors={"missing": str(e)}
            )

        try:
            user, token = UserService.login(username, password)

            if not user:
                return api_response(
                    success=False,
                    code=status.HTTP_401_UNAUTHORIZED,
                    message="Invalid credentials"
                )

            user_data = user.to_dict()
            user_data.pop("password", None)

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="Login successful",
                data={
                    "user": user_data,
                    "token": token
                }
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Login failed",
                errors={"detail": str(e)}
            )

class CreateUserAPI(APIView):

    def post(self, request):
        # validate requesting user
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token"
            )

        try:
            name = request.data["name"]
            username = request.data["username"]
            password = request.data["password"]
            role = request.data.get("role", "viewer")

        except KeyError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Missing required fields",
                errors={"missing": str(e)}
            )

        try:
            new_user = UserService.createUser(
                request_user=request_user,
                name=name,
                username=username,
                password=password,
                role=role
            )

            data = new_user.to_dict()
            data.pop("password", None)

            return api_response(
                success=True,
                code=status.HTTP_201_CREATED,
                message="User created successfully",
                data=data
            )

        except PermissionError as e:
            return api_response(
                success=False,
                code=status.HTTP_403_FORBIDDEN,
                message="Permission denied",
                errors={"detail": str(e)}
            )

        except ValueError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Validation error",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong",
                errors={"detail": str(e)}
            )
            
class DeleteUserAPI(APIView):

    def delete(self, request):
        # validate requesting user
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token"
            )

        try:
            username = request.data["username"]

        except KeyError:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Username is required",
                errors={"missing": "username"}
            )

        try:
            UserService.deleteUser(
                request_user=request_user,
                username=username
            )

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="User deleted successfully"
            )

        except PermissionError as e:
            return api_response(
                success=False,
                code=status.HTTP_403_FORBIDDEN,
                message="Permission denied",
                errors={"detail": str(e)}
            )

        except ValueError as e:
            return api_response(
                success=False,
                code=status.HTTP_404_NOT_FOUND,
                message="User not found",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong",
                errors={"detail": str(e)}
            )
            
class UpdateUserRoleAPI(APIView):

    def put(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token"
            )

        try:
            username = request.data["username"]
            role = request.data["role"]

        except KeyError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Missing required fields",
                errors={"missing": str(e)}
            )

        try:
            updated_user = UserService.updateUser(
                request_user=request_user,
                username=username,
                role=role,
                status=None
            )

            data = updated_user.to_dict()
            data.pop("password", None)

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="User role updated successfully",
                data=data
            )

        except PermissionError as e:
            return api_response(
                success=False,
                code=status.HTTP_403_FORBIDDEN,
                message="Permission denied",
                errors={"detail": str(e)}
            )

        except ValueError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Validation error",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong",
                errors={"detail": str(e)}
            )

class UpdateUserStatusAPI(APIView):

    def put(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token"
            )

        try:
            username = request.data["username"]
            status_value = request.data["status"]

        except KeyError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Missing required fields",
                errors={"missing": str(e)}
            )

        try:
            updated_user = UserService.updateUser(
                request_user=request_user,
                username=username,
                role=None,
                status=status_value
            )

            data = updated_user.to_dict()
            data.pop("password", None)

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="User status updated successfully",
                data=data
            )

        except PermissionError as e:
            return api_response(
                success=False,
                code=status.HTTP_403_FORBIDDEN,
                message="Permission denied",
                errors={"detail": str(e)}
            )

        except ValueError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Validation error",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong",
                errors={"detail": str(e)}
            )
            
class ListUsersAPI(APIView):

    def get(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token"
            )

        try:
            users = UserService.listAllUsers(request_user)

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="Users fetched successfully",
                data=users
            )

        except PermissionError as e:
            return api_response(
                success=False,
                code=status.HTTP_403_FORBIDDEN,
                message="Permission denied",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Something went wrong",
                errors={"detail": str(e)}
            )