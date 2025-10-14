from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginp, name='loginp'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout_view'),  # name matches template
    path('some/post/url/', views.some_post_view, name='some_post_view'), 
    path('api/holidays/', views.holidays_api, name='holidays_api'),  # new API endpoint
]