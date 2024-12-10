from django.db import models
import random
import math

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_login = models.CharField(max_length=150, unique=True)
    user_password = models.CharField(max_length=128)
    user_mail = models.EmailField(unique=True)
    user_date_new = models.DateTimeField(auto_now_add=True)
    user_date_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_login
    
    
class Stat(models.Model):
    strength = models.IntegerField()
    magic = models.IntegerField()
    agility = models.IntegerField()
    speed = models.IntegerField()
    charisma = models.IntegerField()
    chance = models.IntegerField()
    endurance = models.IntegerField()
    life_point = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.endurance = random.randint(self.strength + self.agility, 2 * (self.strength + self.agility))
            self.life_point = random.randint(self.endurance, 2 * self.endurance)
            self.attack = self.strength + self.magic + self.agility
            self.defense = self.agility + self.speed + self.endurance
        super().save(*args, **kwargs)
        
class Classe(models.Model):
    name = models.CharField(max_length=100)
    stat = models.OneToOneField(Stat, on_delete=models.CASCADE)
    
class Race(models.Model):
    name = models.CharField(max_length=100)
    stat = models.OneToOneField(Stat, on_delete=models.CASCADE)
    
class Avatar(models.Model):
    name = models.CharField(max_length=100)
    race = models.ForeignKey(Race, on_delete=models.CASCADE) # création avant
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE) # création avant 
    element = models.CharField(max_length=100) #?
    lvl = models.IntegerField(default=1)
    stat = models.OneToOneField(Stat, on_delete=models.CASCADE)
    life = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.stat = Stat.objects.create(
                strength=1, magic=1, agility=1, speed=1, charisma=0, chance=0
            )
            self.life = self.stat.life_point
        super().save(*args, **kwargs)

        
        
class Hero(Avatar):
    hero_id = models.AutoField(primary_key=True)
    xp = models.IntegerField(default=1)
    profession = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heroes')
    bag = models.OneToOneField('Bag', on_delete=models.CASCADE, related_name='hero_bag', null=True)
    equipment = models.OneToOneField('Equipment', on_delete=models.CASCADE, related_name='hero_equipment', null=True)

    def get_level(self):
        level = math.floor(self.xp / 100)
        if level < 1:
            level = 1
        if level > self.lvl:
            self.level_up()
        return level

    def level_up(self):
        for field in self.stat._meta.fields:
            if field.name not in ['id', 'avatar']:
                setattr(self.stat, field.name, getattr(self.stat, field.name) + 5)
        self.life = self.stat.life_point
        self.stat.save()

    def set_xp(self, xp):
        self.xp += xp
        self.lvl = self.get_level()
        
        
class Item(models.Model):
    TYPE_CHOICES = [
        ('potion', 'Potion'),
        ('plante', 'Plante'),
        ('arme', 'Arme'),
        ('clé', 'Clé'),
        ('armure', 'Pièce d’armure'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    space = models.IntegerField()
    quantity = models.IntegerField()
    stat = models.OneToOneField('Stat', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Equipment(Item):
    class_list = models.JSONField()  # Assuming class_list is a JSON field
    place = models.CharField(max_length=100)
    hero = models.OneToOneField('Hero', on_delete=models.CASCADE, related_name='hero_equipment')

class Bag(models.Model):
    size_max = models.IntegerField()
    items = models.ManyToManyField(Item, related_name='bags_containing_item')
    size = models.IntegerField(default=0)
    hero = models.OneToOneField('Hero', on_delete=models.CASCADE, related_name='hero_bag')

    def add_item(self, item):
        if self.size < self.size_max:
            self.items.add(item)
            self.size += 1
            self.save()
            return True
        return False

    def del_item(self, item):
        self.items.remove(item)
        self.size -= 1
        self.save()
