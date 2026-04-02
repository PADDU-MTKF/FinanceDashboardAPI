from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.parsers import MultiPartParser, FormParser

from .modules.userClass import User,UserService
from .modules.transactionClass import Transaction,TransactionService


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

# User Management APIs **********************************************************************************

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
            

# Transaction Management APIs **************************************************************************

class AddTransactionAPI(APIView):

    def post(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token")

        try:
            amount = float(request.data["amount"])
            t_type = request.data["type"]
            category = request.data["category"]
            notes = request.data.get("notes", "")

        except KeyError as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Missing fields",
                errors={"missing": str(e)}
            )

        try:
            txn = TransactionService.addTransaction(request_user, amount, t_type, category, notes)

            return api_response(
                success=True,
                code=status.HTTP_201_CREATED,
                message="Transaction added",
                data=txn.to_dict()
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
                code=status.HTTP_400_BAD_REQUEST,
                message="Error",
                errors={"detail": str(e)}
            )
            
class UpdateTransactionAPI(APIView):

    def put(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token")

        try:
            tid = request.data["tid"]

        except KeyError:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Transaction ID required"
            )

        try:
            # build dynamic update payload
            update_fields = {}

            if "amount" in request.data:
                update_fields["amount"] = request.data["amount"]

            if "type" in request.data:
                update_fields["t_type"] = request.data["type"]

            if "category" in request.data:
                update_fields["category"] = request.data["category"]

            if "notes" in request.data:
                update_fields["notes"] = request.data["notes"]

            # no fields passed
            if not update_fields:
                return api_response(
                    success=False,
                    code=status.HTTP_400_BAD_REQUEST,
                    message="No fields provided to update"
                )

            txn = TransactionService.updateTransaction(
                request_user,
                tid,
                **update_fields
            )

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="Transaction updated",
                data=txn.to_dict()
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
                message="Not found",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Error",
                errors={"detail": str(e)}
            )
            
class DeleteTransactionAPI(APIView):

    def delete(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token")

        try:
            tid = request.data["tid"]

        except KeyError:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Transaction ID required"
            )

        try:
            TransactionService.deleteTransaction(request_user, tid)

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="Transaction deleted"
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
                message="Not found",
                errors={"detail": str(e)}
            )

        except Exception as e:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Error",
                errors={"detail": str(e)}
            )
            
class GetTransactionAPI(APIView):

    def get(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response(
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token")

        try:
            page = int(request.GET.get("page", 0))
            limit = int(request.GET.get("limit", 10))

            filters = {}
            if request.GET.get("type"):
                filters["type"] = request.GET.get("type")

            if request.GET.get("category"):
                filters["category"] = request.GET.get("category")

        except Exception:
            return api_response(
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                message="Invalid query params"
            )

        try:
            data = TransactionService.getTransaction(
                request_user, page, limit, filters
            )

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="Transactions fetched",
                data=data
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
                code=status.HTTP_400_BAD_REQUEST,
                message="Error",
                errors={"detail": str(e)}
            )
            
class TransactionInsightsAPI(APIView):

    def get(self, request):
        request_user = get_request_user(request)

        if not request_user:
            return api_response( 
                success=False,
                code=status.HTTP_401_UNAUTHORIZED,
                message="Unauthorized - Invalid or missing token")

        try:
            data = TransactionService.getInsights(request_user)

            return api_response(
                success=True,
                code=status.HTTP_200_OK,
                message="Insights fetched",
                data=data
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
                code=status.HTTP_400_BAD_REQUEST,
                message="Error",
                errors={"detail": str(e)}
            )