from django.utils import timezone
from rest_framework import serializers

from job_board.models import ResetPassword, Candidate


class ValidCandidateEmail:
    def __call__(self, value):
        if not Candidate.objects.filter(email=value).first():
            raise serializers.ValidationError(
                'Your given email is not found in candidate list, please insert a valid email address')


class SendOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[ValidCandidateEmail()])

    class Meta:
        model = ResetPassword
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[ValidCandidateEmail()])
    otp = serializers.CharField(min_length=6, max_length=6)
    password = serializers.CharField(min_length=6, max_length=40)

    def validate(self, data):
        if ResetPassword.objects.filter(
                otp_used_at__isnull=True,
                email__exact=data['email'],
                otp__exact=data['otp'],
                otp_expire_at__gte=timezone.now()).last():
            return data
        raise serializers.ValidationError({'otp': 'OTP is not correct or expire'})

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        candidate = Candidate.objects.filter(email__exact=validated_data['email']).first()
        candidate.password = validated_data['password']
        candidate.save()

        pass_reset = ResetPassword.objects.filter(otp__exact=validated_data['otp']).last()
        pass_reset.otp_used_at = timezone.now()
        pass_reset.save()
        return validated_data
