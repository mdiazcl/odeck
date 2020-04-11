from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import *

# Register your models here.
admin.site.register(Deck)
admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Graveyard)
admin.site.register(Hand)

class CardModel(admin.ModelAdmin):
    list_display = ('suit','number','deck','graveyard','get_location')
    search_fields = ['get_location']
admin.site.register(Card, CardModel)

