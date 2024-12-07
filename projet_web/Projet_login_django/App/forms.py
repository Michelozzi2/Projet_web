from django import forms  # Importe le module de formulaires de Django
from .models import User

# Définition d'un formulaire de connexion personnalisé.
# Ce formulaire contient deux champs : un pour le nom d'utilisateur et un pour le mot de passe.

class LoginForm(forms.Form):
    # Champ pour le nom d'utilisateur avec une longueur maximale de 100 caractères.
    username = forms.CharField(label="Nom d'utilisateur", max_length=100)

    # Champ pour le mot de passe. Le widget 'PasswordInput' masque le texte entré.
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class SignUpForm(forms.ModelForm):
    class Meta:
        model = User  # Utilise le modèle User pour ce formulaire
        fields = ['user_login', 'user_password', 'user_mail']  # Champs du formulaire
        widgets = {
            'user_login': forms.TextInput(),  # Champ de texte pour le nom d'utilisateur
            'user_mail': forms.TextInput(),    # Champ de texte pour l'email
            'user_password': forms.PasswordInput(),  # Champ de mot de passe
        }
        labels = {
            'user_login': 'Nom d\'utilisateur',  # Étiquette pour le champ nom d'utilisateur
            'user_mail': 'Email',                  # Étiquette pour le champ email
            'user_password': 'Mot de passe',       # Étiquette pour le champ mot de passe
        }
    user_password = forms.CharField(widget=forms.PasswordInput)  # Masque le mot de passe

from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'type', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nom de l\'objet'}),  
            'type': forms.Select(choices=Item.TYPE_CHOICES),  # Utilisation d'une liste déroulante pour le type
            'quantity': forms.NumberInput(attrs={'placeholder': 'Quantité'}),
        }
        labels = {
            'name': 'Nom de l\'objet',  
            'type': 'Type de l\'objet',                  
            'quantity': 'Quantité',      
        }