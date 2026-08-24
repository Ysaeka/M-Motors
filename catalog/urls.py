from django.urls import path

from .views import vehicle_detail, vehicle_list

urlpatterns = [
    path("", vehicle_list, name="vehicle_list"),
    path("<int:pk>/", vehicle_detail, name="vehicle_detail"),
]