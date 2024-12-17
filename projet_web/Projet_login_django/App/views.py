import random
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
            user.user_password = make_password(form.cleaned_data['user_password'])  # Chiffre le mot de passe
            user.save()
            messages.success(request, "Votre inscription a été réalisée avec succès !")
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'App/signup.html', {'form': form})


# Vue pour afficher la liste des objets d'inventaire
def hero_inventory(request, hero_id):
    hero = get_object_or_404(Hero, id=hero_id, user=request.session.get('user_id'))

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


# ...existing code...

def combat_view(request, hero1_id, hero2_id):
    hero1 = get_object_or_404(Hero, id=hero1_id, user=request.session.get('user_id'))
    hero2 = get_object_or_404(Hero, id=hero2_id)
    
    def calculate_damage(attacker, defender):
        base_damage = attacker.stat.attack
        random_modifier = random.uniform(0.8, 1.2)
        damage_reduction = defender.stat.defense / 100
        return max(1, int((base_damage * random_modifier) * (1 - damage_reduction)))

    if request.method == 'POST':
        # Logique de tour de combat via AJAX
        attacker = hero1 if request.POST.get('attacker') == str(hero1.id) else hero2
        defender = hero2 if attacker == hero1 else hero1
        
        # Calcul de l'initiative
        if random.randint(1, attacker.stat.speed + defender.stat.speed) <= attacker.stat.speed:
            damage = calculate_damage(attacker, defender)
            defender.life -= damage
            defender.save()
            
            if defender.life <= 0:
                winner = attacker
                return JsonResponse({
                    'finished': True,
                    'winner': winner.name,
                    'message': f"{winner.name} a gagné le combat!"
                })
            
            return JsonResponse({
                'damage': damage,
                'defender_life': defender.life,
                'attacker': attacker.name,
                'defender': defender.name
            })
            
        return JsonResponse({'missed': True})

    # Réinitialiser les PV au début du combat
    hero1.life = hero1.stat.life_point
    hero2.life = hero2.stat.life_point
    hero1.save()
    hero2.save()
    
    return render(request, 'App/combat.html', {
        'hero1': hero1,
        'hero2': hero2
    })
