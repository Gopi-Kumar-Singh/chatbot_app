from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("chatbot", views.chatbot, name="chatbot"),
    path("performanceMonitor", views.performance_monitor, name="performanceMonitor"),
    path("shareDataWithSalesTeam", views.share_user_data_with_sales_team, name="shareDataWithSalesTeam")
]