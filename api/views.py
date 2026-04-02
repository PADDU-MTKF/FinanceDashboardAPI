from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

# from .modules.login import *
# from .modules.events import *

# from  .modules.utility import checkReq 

@api_view(['GET'])
def home(request):
    data={"Status": "Ok"}
    return Response(data)
