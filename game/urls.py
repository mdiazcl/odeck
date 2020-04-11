# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('games/', my_games, name="game_list"),
    path('games/create', create_game, name="game_create"),
    path('games/join', join_game, name="game_join"),
    path('game/<int:game_id>/play', play_game, name="game_play"),

    # api part
    path('game/<int:game_id>/draw/<str:location>', api_draw_card, name="api_draw_card"),
    path('game/<int:game_id>/put/graveyard/<str:card_id>', api_put_card_graveyard, name="api_put_card_graveyard"),
    path('game/<int:game_id>/put/myfield/<str:card_id>', api_put_card_field, name="api_put_card_field"),
    path('game/<int:game_id>/put/myhand/<str:card_id>', api_put_card_hand, name="api_put_card_hand"),
    
    path('game/<int:game_id>/get_my_hand', api_get_my_hand, name="api_get_my_hand"),
    path('game/<int:game_id>/get_my_field', api_get_my_field, name="api_get_my_field"),
    path('game/<int:game_id>/get_oponent_field', api_get_oponent_field, name="api_get_oponent_field"),
    path('game/<int:game_id>/get_graveyard', api_get_graveyard, name="api_get_graveyard"),
    path('game/<int:game_id>/count_oponent_hand', api_count_oponent_hand, name="api_count_oponent_hand"),

    path('logout/', logout_view, name = "logout"),
    path('', login_view, name = "login"),
]