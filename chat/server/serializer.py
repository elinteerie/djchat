from rest_framework import serializers
from .models import Server, Category, Channel


class ChannelSerializer(serializers.ModelSerializer):
     class Meta:
        model = Channel
        fields = "__all__"

class ServerSerializer(serializers.ModelSerializer):
    num_numbers = serializers.SerializerMethodField()
    channel_server = ChannelSerializer(many=True)
    class Meta:
        model = Server
        exclude = ("members",)
        
        
    def get_num_numbers(self, obj):
        if hasattr(obj, "num_numbers"):
            return obj.num_numbers
        return None
        
