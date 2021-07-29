from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from job_board.auth.CandidateAuth import CandidateAuth, CredentialsSerializer
from job_board.models import Candidate
from job_board.serializers.candidate_serializer import CandidateSerializer, CandidateUpdateSerializer
from job_board.serializers.password_reset import SendOTPSerializer, ResetPasswordSerializer


class Registration(CreateModelMixin, GenericAPIView):
    """
    Candidate registration requires a form data with
    """
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class Login(GenericAPIView, CreateModelMixin):
    """
    Candidate Login

    candidate only can able to login with email & password

    send a post request with a valid json format { "email" : "<your@email>", "password": "<your password>" }
    """

    serializer_class = CredentialsSerializer

    def post(self, request, format=None):
        auth = CandidateAuth()
        return auth.auth_token(request)


class User(APIView):
    """
    Candidate information
    TODO : update profile update will be in post method
    """
    authentication_classes = [CandidateAuth]

    def get(self, request, format=None):
        serialize = CandidateSerializer(request.user, context={"request": request})
        return Response(serialize.data)

    def post(self, request, format=None):
        serialize = CandidateUpdateSerializer(data=request.data)
        if serialize.is_valid():
            serialize.update(instance=request.user, validated_data=serialize.validated_data)
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTP(GenericAPIView, CreateModelMixin):
    serializer_class = SendOTPSerializer
    queryset = Candidate.objects.all()

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'message': 'OTP has been sent'}, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView, CreateModelMixin):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'message': 'Candidate password has been updated successfully'})


class ChangeCandidatePassword(GenericAPIView):
    authentication_classes = [CandidateAuth]
