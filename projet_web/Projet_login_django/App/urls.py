from django.urls import path
from django.contrib.auth import views as auth_views

 # Importe les vues définies dans le fichier views.py
from .views import login_view, home_view, signup_view
from .views import create_hero, hero_list, hero_inventory, combat_view

# Définition des URL pour l'application. 
# Chaque URL est liée à une vue spécifique qui gère la logique pour cette route.

urlpatterns = [
    path('login/', login_view, name='login'),
    path("", home_view, name="home"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', signup_view, name='signup'),  # URL pour la page d'inscription
    path('hero/', create_hero, name='create_hero'),
    path('hero_list/', hero_list, name='hero_list'),
    path('hero/<int:hero_id>/inventory/', hero_inventory, name='hero_inventory'),
    path('combat/<int:hero1_id>/<int:hero2_id>/', combat_view, name='combat'),
]
