from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .forms import *
from .models import *

# Create your views here.
def login_view(request):   
    context = {}

    if request.user.is_authenticated:
        return redirect('game_list')

    form = FormLogin()

    if request.method == "POST":
        form = FormLogin(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']

            user = authenticate(username = user, password = password)
            
            if user is not None:
                login(request, user)
                return redirect('game_list')
    
    context['form'] = form
    return render(request, 'game/login.html', context = context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def my_games(request):
    context = {}

    # Base Views
    current_player = Player.GetPlayer(request.user)

    # Custom Data
    my_games = current_player.get_owned_games()
    guest_games = current_player.get_guest_games()
    context['form'] = FormJoinGame()

    if len(my_games) > 0:
        context['mygames'] = my_games
    if len(guest_games) > 0:
        context['guestgames'] = guest_games

    return render(request, 'game/my_games.html', context = context)

@login_required
def create_game(request):
    context = {}

    # Base Views
    current_player = Player.GetPlayer(request.user)

    form = FormNewGame()
    if request.method == "POST":
        form = FormNewGame(request.POST)
        if form.is_valid():
            # Create game
            name = form.cleaned_data['name']
            game = Game.CreateGame(current_player, name, deck_count = 2)
            messages.success(request, 'Juego creado correctamente!')
            return redirect('game_list')
        
    context['form'] = form

    return render(request, 'game/create_game.html', context = context)

@login_required
def join_game(request):
    context = {}

    # Base Views
    current_player = Player.GetPlayer(request.user)

    # Custom Data
    if request.method == "POST":
        form = FormJoinGame(request.POST)
        if form.is_valid():
            room_id = form.cleaned_data['gid']
            room_pwd = form.cleaned_data['password']
            result_game = Game.JoinGame(current_player, room_id, room_pwd)
            if result_game == 500:
                # your game
                messages.error(request, 'No puedes jugar contra ti mismo!')
            elif result_game == 501:
                # your game
                messages.error(request, 'El juego esta lleno! :(')
            elif result_game == 200:
                # success
                messages.success(request, 'Se ha unido al juego!')
            else:
                # ocurrio un error
                messages.error(request, 'Algo paso :( - {}'.format(result_game))

            return redirect('game_list')

@login_required
def play_game(request, game_id):
    context = {}

    # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)

    player_owner = game.player_owner
    player_guest = game.player_guest

    # Check que hay contrincante
    if(player_guest is None):
        messages.error(request, 'Espera a que entre el otro jugador! Dale los datos de la partida!')
        return redirect('game_list')

    # Load Game
    context['game'] = game
    context['player_owner'] = player_owner
    context['player_guest'] = player_guest

    return render(request, 'game/gameroom.html', context = context)

#########
# API CALLS
def get_player_side(game, player):
    response = {}
    if player == game.player_owner:
        player = 0
        response['played_called'] = "owner"
    elif player == game.player_guest:
        player = 1
        response['played_called'] = "guest"
    else:
        response['error'] = response['error'].append("Can't find player.")
    
    return response, player

@login_required
def api_draw_card(request, game_id, location):
    response = {}
    response['apicall'] = "draw_card"
    error = []

    # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)
    
    # Get Player asking (0 = owner, 1 = guest)
    result, player = get_player_side(game, current_player)
    response = {**response, **result}
    
    response['error'] = error
    response['result'] = game.draw_card(location, player)

    return JsonResponse(response)

@login_required
def api_get_my_hand(request, game_id):
    response = {}
    response['apicall'] = "get_my_hand"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)

    # Get Player asking (0 = owner, 1 = guest)
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    if player == 0:
        cards = game.player_owner_hand.get_cards()
    else:
        cards = game.player_guest_hand.get_cards()

    result_cards = []
    for card in cards:
        dict_card = {}
        dict_card['number'] = card.number
        dict_card['suit'] = card.suit
        dict_card['image'] = card.get_image_filename()
        dict_card['id'] = card.pk
        result_cards.append(dict_card)
    
    response['data'] = result_cards
    response['error'] = error

    return JsonResponse(response)

@login_required
def api_get_my_field(request, game_id):
    response = {}
    response['apicall'] = "get_my_field"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)

    # Get Player asking (0 = owner, 1 = guest)
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    if player == 0:
        cards = game.player_owner_field.get_cards()
    else:
        cards = game.player_guest_field.get_cards()

    result_cards = []
    for card in cards:
        dict_card = {}
        dict_card['number'] = card.number
        dict_card['suit'] = card.suit
        dict_card['image'] = card.get_image_filename()
        dict_card['id'] = card.pk
        result_cards.append(dict_card)
    
    response['data'] = result_cards
    response['error'] = error

    return JsonResponse(response)

@login_required
def api_get_oponent_field(request, game_id):
    response = {}
    response['apicall'] = "get_oponent_field"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)

    # Get Player asking (0 = owner, 1 = guest)
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    if player == 1:
        cards = game.player_owner_field.get_cards()
    else:
        cards = game.player_guest_field.get_cards()

    result_cards = []
    for card in cards:
        dict_card = {}
        dict_card['number'] = card.number
        dict_card['suit'] = card.suit
        dict_card['image'] = card.get_image_filename()
        dict_card['id'] = card.pk
        result_cards.append(dict_card)
    
    response['data'] = result_cards
    response['error'] = error

    return JsonResponse(response)

@login_required
def api_get_graveyard(request, game_id):
    response = {}
    response['apicall'] = "get_graveyard"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)

    # Get Player asking (0 = owner, 1 = guest)
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    dict_card = {}
    top_card = game.graveyard.get_top_card(remove = False)
    
    result_cards = []
    if top_card is not None and len(top_card) > 0:
        top_card = top_card[0]
        dict_card = {}
        dict_card['number'] = top_card.number
        dict_card['suit'] = top_card.suit
        dict_card['image'] = top_card.get_image_filename()
        dict_card['id'] = top_card.pk
        result_cards.append(dict_card)
    
    response['data'] = result_cards
    response['error'] = error

    return JsonResponse(response)

@login_required
def api_count_oponent_hand(request, game_id):
    response = {}
    response['apicall'] = "count_oponent_hand"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)

    # Get Player asking (0 = owner, 1 = guest)
    result, player = get_player_side(game, current_player)
    response = {**response, **result}
      
    game = get_object_or_404(Game, pk = game_id)

    if player == 1:
        cards = game.player_owner_hand.get_cards()
    else:
        cards = game.player_guest_hand.get_cards()

    response['data'] = len(cards)
    response['error'] = error

    return JsonResponse(response)

@login_required
def api_put_card_graveyard(request, game_id, card_id):
    response = {}
    response['apicall'] = "put_card_graveyard"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)
    card = get_object_or_404(Card, pk = card_id)

    # Check if you have the card
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    if player == 0:
        in_hand = game.player_owner_hand.have_card(card)
        in_field = game.player_owner_field.have_card(card)
        have_card = in_hand | in_field
    else:
        in_hand = game.player_guest_hand.have_card(card)
        in_field = game.player_guest_field.have_card(card)
        have_card = in_hand | in_field
    
    # Put in graveyard
    if not have_card:
        error.append('No tienes esa carta en tu mano!')
    else:
        game.put_card(card, "graveyard")
        response['result'] = True

    response['error'] = error

    return JsonResponse(response)

@login_required
def api_put_card_field(request, game_id, card_id):
    response = {}
    response['apicall'] = "put_card_field"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)
    card = get_object_or_404(Card, pk = card_id)

    # Check if you have the card
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    if player == 0:
        have_card = game.player_owner_hand.have_card(card)
        location = "owner_field"
    else:
        have_card = game.player_guest_hand.have_card(card)
        location = "guest_field"
    
    # Put in graveyard
    if not have_card:
        error.append('No tienes esa carta en tu mano!')
    else:
        game.put_card(card, location)
        response['result'] = True

    response['error'] = error

    return JsonResponse(response)

@login_required
def api_put_card_hand(request, game_id, card_id):
    response = {}
    response['apicall'] = "api_put_card_hand"
    error = []

     # Base Views
    current_player = Player.GetPlayer(request.user)
    game = get_object_or_404(Game, pk = game_id)
    card = get_object_or_404(Card, pk = card_id)

    # Check if you have the card
    result, player = get_player_side(game, current_player)
    response = {**response, **result}

    if player == 0:
        in_field = game.player_owner_field.have_card(card)
        in_graveyard =  game.graveyard.is_top_card(card)
        have_card = in_field | in_graveyard
        location = "owner_hand"
    else:
        in_field = game.player_guest_field.have_card(card)
        in_graveyard =  game.graveyard.is_top_card(card)
        have_card = in_field | in_graveyard
        location = "guest_hand"
    
    # Put in graveyard
    if not have_card:
        error.append('Esta carta no esta en tu campo ni en el cementerio!')
    else:
        game.put_card(card, location)
        response['result'] = True

    response['error'] = error

    return JsonResponse(response)