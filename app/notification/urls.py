from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.notification.views import NotificationReadAPI, NotificationViewSet, OrderStatusUpdateView

router = DefaultRouter()
router.register("notifications", NotificationViewSet, basename='notifications')

read_view = NotificationReadAPI.as_view({"patch" : "partial_update"})

urlpatterns = [
    path("notifications/<int:pk>/read", read_view, name="notification-read"),
    path('', include(router.urls)),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]

urlpatterns += router.urls

