from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class InitialView(APIView):
    # Isso é apenas um teste
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Endpoint working!"})
