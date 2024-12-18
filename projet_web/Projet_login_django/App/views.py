import random
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import SignUpForm, HeroForm
from .models import Equipment, Item, User, Hero
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.template.loader import render_to_string


# Vue pour la page de connexion
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Récupère l'utilisateur par son nom d'utilisateur
            user = User.objects.get(user_login=username)

            # Utilise check_password pour comparer le mot de passe entré avec le mot de passe haché
            if check_password(password, user.user_password):
                # Si correct, stocke l'ID utilisateur et le login dans la session
                request.session['user_id'] = user.user_id
                request.session['user_login'] = user.user_login
                return redirect('home')
            else:
                # Mot de passe incorrect
                messages.error(request, 'Mot de passe incorrect')
        except User.DoesNotExist:
            # Utilisateur non trouvé
            messages.error(request, 'Utilisateur non trouvé')

    # Affiche la page de connexion pour GET ou en cas d'erreur
    return render(request, 'App/login.html')


# Vue pour la page d'accueil (après connexion)
def home_view(request):

    # Récupère le login de l'utilisateur à partir de la session
    user_login = request.session.get('user_login')

    # Si l'utilisateur est connecté, affiche la page d'accueil avec son login
    if user_login:
        return render(request, 'App/home.html', {'user_login': user_login})
    else:
        # Si l'utilisateur n'est pas connecté, redirige vers la page de connexion
        return redirect('login')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_password = make_password(
                form.cleaned_data['user_password'])  # Chiffre le mot de passe
            user.save()
            messages.success(
                request, "Votre inscription a été réalisée avec succès !")
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'App/signup.html', {'form': form})


# Vue pour afficher la liste des objets d'inventaire
def hero_inventory(request, hero_id):
    hero = get_object_or_404(
        Hero, id=hero_id, user=request.session.get('user_id'))

    # Filtrer les objets et équipements par héros
    items = Item.objects.filter(bags_containing_item__hero=hero)
    equipments = Equipment.objects.filter(hero=hero)

    # Rechercher par nom
    search_query = request.GET.get('search', '')
    if search_query:
        items = items.filter(name__icontains=search_query)
        equipments = equipments.filter(name__icontains=search_query)

    # Trier par type
    sort_query = request.GET.get('sort', '')
    if sort_query:
        if sort_query == 'item':
            equipments = Equipment.objects.none()
        elif sort_query == 'equipment':
            items = Item.objects.none()

    # Requête AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        context = {'items': items, 'equipments': equipments}
        items_html = render_to_string('App/inventory_table.html', context)
        return JsonResponse({'items_html': items_html})

    # Rendu normal
    return render(request, 'App/hero_inventory.html', {
        'hero': hero,
        'items': items,
        'equipments': equipments
    })


def create_hero(request):
    user_id = request.session.get('user_id')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur n'existe pas.")
        return redirect('home')

    if request.method == 'POST':
        form = HeroForm(request.POST)

        if form.is_valid():
            hero = form.save(commit=False)
            hero.user = user
            hero.save()
            messages.success(request, 'Héros créé avec succès.')
            return redirect('home')
    else:
        form = HeroForm()

    return render(request, 'App/create_hero.html', {'form': form})


def hero_list(request):
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur n'existe pas.")
        return redirect('home')

    heroes = user.heroes.all()
    return render(request, 'App/hero_list.html', {'heroes': heroes})


def combat_view(request, hero1_id, hero2_id):
    # Récupérer les héros et vérifier qu'ils appartiennent à l'utilisateur
    hero1 = get_object_or_404(
        Hero, id=hero1_id, user=request.session.get('user_id'))
    hero2 = get_object_or_404(
        Hero, id=hero2_id, user=request.session.get('user_id'))

    # Stocker les IDs des héros dans la session pour attack_view
    request.session['hero1_id'] = hero1.id
    request.session['hero2_id'] = hero2.id

    # Réinitialiser les PV au début du combat
    hero1.life = hero1.stat.life_point
    hero2.life = hero2.stat.life_point
    hero1.save()
    hero2.save()

    return render(request, 'App/combat.html', {
        'hero1': hero1,
        'hero2': hero2
    })


def attack_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    # Récupérer les héros de la session
    hero1 = get_object_or_404(Hero, id=request.session.get('hero1_id'))
    hero2 = get_object_or_404(Hero, id=request.session.get('hero2_id'))

    # Récupérer le tour actuel de la session ou initialiser à 1
    current_turn = request.session.get('combat_turn', 1)
    
    # Déterminer l'attaquant basé sur le tour
    attacker = hero1 if current_turn % 2 == 1 else hero2
    defender = hero2 if current_turn % 2 == 1 else hero1

    # Calculer si l'attaque réussit (basé sur la vitesse)
    hit_chance = min(90, attacker.stat.speed + 50)  
    if random.randint(1, 100) <= hit_chance:
        # Calculer les dégâts
        base_damage = attacker.stat.attack
        random_modifier = random.uniform(0.8, 1.2)
        defense_reduction = min(0.75, defender.stat.defense / 100) 
        damage = max(1, int((base_damage * random_modifier) * (1 - defense_reduction)))

        # Appliquer les dégâts
        defender.life = max(0, defender.life - damage)
        defender.save()

        # Vérifier si le combat est terminé
        if defender.life <= 0:
            # Réinitialiser le tour de combat
            request.session.pop('combat_turn', None)
            
            # Donner de l'XP au gagnant
            xp_gain = 50 + (defender.lvl * 10)
            attacker.set_xp(xp_gain)
            attacker.save()

            return JsonResponse({
                'finished': True,
                'message': f"{attacker.name} a gagné le combat et gagne {xp_gain} XP!",
                'defender_life': 0,
                'winner': attacker.name,
                'xp_gain': xp_gain
            })

        # Incrémenter le tour
        request.session['combat_turn'] = current_turn + 1

        return JsonResponse({
            'damage': damage,
            'attacker': attacker.name,
            'defender': defender.name,
            'defender_life': defender.life,
            'turn': current_turn
        })

    # Incrémenter le tour même en cas d'échec
    request.session['combat_turn'] = current_turn + 1
    
    return JsonResponse({
        'missed': True,
        'attacker': attacker.name,
        'defender': defender.name,
        'turn': current_turn
    })