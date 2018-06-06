from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name="index"),
    path('member/<member_name>', views.view_member_profile, name="member_profile"),
    path('member/<member_name>/signin', views.member_signin, name="member_signin"),
    path('member/<member_name>/signout', views.member_signout, name="member_signout"),
    path('member/<member_name>/correction', views.member_time_correction, name="member_time_correction"),
    path('whos_in', views.whos_in, name="whos_in")
]
