from django.urls import path, include
from .views import (
    RegisterView,
    CustomLoginView,
    CustomLogoutView,
    ProfileView

)
from apps.auth_app.adapters.web import views

app_name = 'auth'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    path('profiles/', views.profiles_list, name='profiles_list'),
    path('profiles/<uuid:pk>/', views.profile_detail, name='profile_detail'),

]