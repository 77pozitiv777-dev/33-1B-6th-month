from rest_framework import serializers 
from app.notification.models import Notification
from app.product.models import Order

class NotificationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title',
            'message', "is_read", "delivered_at",
            'ctreated_at'
        ]

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']