from rest_framework import mixins, status, viewsets, generics
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .models import Notification
from app.product.models import Order
from .serializers import OrderStatusUpdateSerializer, NotificationSerializer
from .tasks import create_notification_task

from app.notification.models import Notification
from app.notification.serializers import NotificationSerializers

class NotificationViewSet(mixins.ListModelMixin,
                    GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializers

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-id")

class NotificationReadAPI(ViewSet):
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, pk=None):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        return Response({"ok": True}, status=status.HTTP_200_OK)

class OrderStatusUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status:
            order.status = new_status
            order.save()
            message = f"Статус вашего заказа №{order.id} изменен на '{new_status}'"
            create_notification_task.delay(order.user.id, message)
            
            return Response({"message": f"Статус изменен на {new_status}"}, status=status.HTTP_200_OK)
        return Response({"error": "Статус не указан"}, status=status.HTTP_400_BAD_REQUEST)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})