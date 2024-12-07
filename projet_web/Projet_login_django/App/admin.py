from django.contrib import admin  # Importe le module d'administration de Django

from .models import Item, User, Stat, Hero, Equipment, Bag, Classe, Race, Avatar  # Importe le modèle 'User' défini dans models.py

# Enregistre le modèle 'User' dans l'interface d'administration de Django.
# Cela permet de gérer les objets 'User' via le panneau d'administration.
admin.site.register(User)
admin.site.register(Item)  # Enregistre le modèle 'Item' dans l'interface d'administration
admin.site.register(Stat)
admin.site.register(Hero)
admin.site.register(Equipment)
admin.site.register(Bag)
admin.site.register(Classe)
admin.site.register(Race)
admin.site.register(Avatar)