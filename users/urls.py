from django.urls import path
from users import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('nlp-preference/', views.get_nlp_preference, name='get_nlp_preference'),
path('nlp-preference/set/', views.set_nlp_preference, name='set_nlp_preference'),
]