import jwt
from django.contrib.auth import hashers
from rest_framework import serializers
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.fields import CharField, EmailField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from job_board.models import Candidate
from job_board.serializers.candidate_serializer import CandidateSerializer


class CredentialsSerializer(Serializer):
    """
    Credentials Serializer
    use for request validation and json response

    @type Serializer : Serializer
    """
    email = CharField()
    password = CharField(max_length=40, min_length=5)


class CandidateAuth(BaseAuthentication):
    """
    Candidate auth
    This class is responsible to create jwt auth token using given credentials
    also it is responsible to register user
    """
    STRONG_SECRET = "rifat"
    ENCRYPT_ALGORITHMS = "HS256"

    # candidate model
    candidate = None

    def authenticate(self, request):
        """
        Validate the given jwt token and process next if matched
        @type request: object
        """
        token = get_authorization_header(request).split()
        if token:
            user = jwt.decode(token[1], self.STRONG_SECRET, algorithms=self.ENCRYPT_ALGORITHMS)
            if user:
                user = Candidate.objects.get(pk=user['id'])
                return user, None
            else:
                raise serializers.ValidationError({'token': f'your token {token[1]} seems not valid'})
        else:
            raise serializers.ValidationError({'token': 'Token Not found'})

    def auth_token(self, request):
        """
        Create auth token using given credentials
        if the data is valid and password is matched with given email address

        @param request:
        @return:
        """
        serializer = CredentialsSerializer(data=request.data)
        if serializer.is_valid() and self.__match_credentials(serializer):
            return self.__generate_token(self.candidate)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def __match_credentials(self, serializer: CredentialsSerializer):
        """
        Match given credentials from serializers
        @raise error if given username / email is not found
        @raise error if given password is not matched with given email / username

        @param serializer:
        @return:
        """
        try:
            candidate = Candidate.objects.get(email__exact=serializer.data['email'])
            if hashers.check_password(serializer.data['password'], candidate.password):
                self.candidate = candidate
                return True
            raise AuthenticationFailed('Credentials does not matched')
        except:
            raise AuthenticationFailed('Credentials does not matched')

    def __generate_token(self, candidate: Candidate):
        """
        Generate JWT token

        @param candidate:
        @return json:
        """
        user_serializer = CandidateSerializer(candidate)
        encoded = jwt.encode(user_serializer.data, self.STRONG_SECRET, algorithm=self.ENCRYPT_ALGORITHMS)
        return Response({'_token': encoded})
