from django.contrib import admin
from django.urls import include, path
from polls.views import acc_list_create, acc_detail

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("polls.urls")),
    path("acc/", acc_list_create),
    path("acc/<int:id>/", acc_detail),
]