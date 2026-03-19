from rest_framework import serializers
from .models import User, Node, Edge, Trip, CarpoolRequest, CarpoolOffer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'


class EdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edge
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['driver', 'route', 'visited_nodes', 'status']


class CarpoolRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarpoolRequest
        fields = '__all__'
        read_only_fields = ['passenger', 'status']


class CarpoolOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarpoolOffer
        fields = '__all__'