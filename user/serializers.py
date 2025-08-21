from .models import MyUser
from rest_framework import serializers

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = MyUser(**validated_data)

        user.set_password(validated_data['password'])
        user.save()

        return user
