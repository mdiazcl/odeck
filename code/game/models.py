from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

import uuid, random

# Create your models here.
class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length = 5)

    # Game Properties
    name = models.CharField(max_length = 12, default = '')
    player_owner = models.ForeignKey('game.Player', on_delete = models.CASCADE, related_name="player1")
    player_owner_hand = models.ForeignKey('game.Hand', on_delete = models.CASCADE, related_name="player1_hand")
    player_owner_field = models.ForeignKey('game.PlayerField', on_delete = models.CASCADE, related_name="player1_field")

    player_guest = models.ForeignKey('game.Player', on_delete = models.CASCADE, related_name="player2", null = True)
    player_guest_hand = models.ForeignKey('game.Hand', on_delete = models.CASCADE, related_name="player2_hand", null = True)
    player_guest_field = models.ForeignKey('game.PlayerField', on_delete = models.CASCADE, related_name="player2_field", null = True)

    deck = models.ForeignKey('game.Deck', on_delete = models.CASCADE)
    graveyard = models.ForeignKey('game.Graveyard', on_delete = models.CASCADE)

    def draw_card(self, from_location, player_hand):
        # Draw From Deck
        if from_location == "deck":
            carta = self.deck.get_random_card()
        elif from_location == "graveyard":
            carta = self.graveyard.get_top_card()
        else:
            return None

        if carta == None:
            return None
        
        # Give card to players hand
        if player_hand == 0:
            self.player_owner_hand.put_card(carta)
            return True
        else:
            self.player_guest_hand.put_card(carta)
            return True

    def put_card(self, carta, target):
        # remove card location
        carta.deck = None
        carta.hand = None
        carta.field = None
        if carta.graveyard is not None:
            self.graveyard.top_card_position -= 1
            self.graveyard.save()
            carta.graveyard = None
        carta.save()

        if target == "owner_field":
            self.player_owner_field.put_card(carta)
        elif target == "guest_field":
            self.player_guest_field.put_card(carta)
        elif target == "deck":
            self.deck.put_card(carta)
        elif target == "guest_hand":
            self.player_guest_hand.put_card(carta)
        elif target == "owner_hand":
            self.player_owner_hand.put_card(carta)
        else:
            # default, graveyard
            self.graveyard.put_card(carta)
    
    def is_ready(self):
        if self.player_guest is not None:
            return True
        return False

    @staticmethod
    def CreateGame(player_owner, game_name = "", deck_count = 2):
        game = Game()
        game.name = game_name
        game.password = random.randrange(10000, 99999)

        # Create basics
        graveyard = Graveyard()
        graveyard.save()

        player_hand = Hand()
        player_hand.save()

        player_field = PlayerField()
        player_field.save()

        game.player_owner = player_owner
        game.deck = Deck.CreateDeck(decks_count = 2)
        game.graveyard = graveyard
        game.player_owner_hand = player_hand
        game.player_owner_field = player_field

        game.save()

        return game

    @staticmethod
    def JoinGame(player_guest, room_id, room_code):
        try:
            game = Game.objects.get(Q(pk = room_id) & Q(password = room_code))

            # Check if you already have a guest player
            if game.player_guest is not None:
                return 501

            # Check if you are not the owner
            if game.player_owner == player_guest:
                return 500

            player_hand = Hand()
            player_hand.save()

            player_field = PlayerField()
            player_field.save()

            game.player_guest = player_guest
            game.player_guest_hand = player_hand
            game.player_guest_field = player_field

            game.save()

            return 200

        except Exception as error:
            return error

class Player(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length=100)

    def get_owned_games(self):
        return Game.objects.filter(player_owner = self).order_by("-pk")[:10]
    def get_guest_games(self):
        return Game.objects.filter(player_guest = self).order_by("-pk")[:10]

    @staticmethod
    def GetPlayer(user):
        return Player.objects.get(user = user)

class Graveyard(models.Model):
    top_card_position = models.IntegerField(default = -1)

    def put_card(self, carta):
        carta.graveyard = self
        carta.graveyard_position = self.get_actual_position() + 1
        carta.save()

        self.top_card_position = self.get_actual_position() + 1
        self.save()

    def is_top_card(self, carta):
        top_card = self.get_top_card(remove = False)
        if len(top_card) > 0:
            top_card = self.get_top_card(remove = False)[0]
            if top_card == carta:
                return True
        return False

    def get_top_card(self, remove = True):
        if self.top_card_position > -1:
            try:
                card = Card.objects.filter(Q(graveyard = self) & Q(graveyard_position = self.top_card_position))
                if remove:
                    card.graveyard = None
                    card.graveyard_position = None
                    card.save()

                    self.top_card_position -= 1
                    self.save()

                return card
            except Exception as e:
                print(e)
                return []
        else:
            return []

    def get_actual_position(self):
        return self.top_card_position

    def get_cards(self):
        return Card.objects.filter(graveyard = self)

class PlayerField(models.Model):
    def put_card(self, carta):
        carta.field = self
        carta.save()

    def have_card(self, carta):
        tiene = len(Card.objects.filter(Q(field = self) & Q(pk = carta.pk)))
        if tiene > 0:
            return True
        else:
            return False

    def get_cards(self):
        return Card.objects.filter(field = self)

class Hand(models.Model):
    def put_card(self, carta):
        carta.hand = self
        carta.save()

    def have_card(self, carta):
        tiene = len(Card.objects.filter(Q(hand = self) & Q(pk = carta.pk)))
        if tiene > 0:
            return True
        else:
            return False

    def get_cards(self):
        return Card.objects.filter(hand = self).order_by('suit')

class Deck(models.Model):
    def put_card(self, carta):
        carta.deck = self
        carta.save()

    def get_cards(self):
        return Card.objects.filter(deck = self)

    def get_random_card(self):
        all_cards = self.get_cards()
        if len(all_cards) <= 0:
            return None

        # Get Random
        random_card = random.choice(all_cards)
        random_card.deck = None
        random_card.save()
        return random_card

    @staticmethod
    def CreateDeck(normal_deck = True, joker = True, joker_count = 2, decks_count = 1):
        # Create empty deck
        deck = Deck()
        deck.save()

        # Create many decks
        for k in range(decks_count):
            # For each suit
            for suit in range(4):
                for number in range(10):
                    card = Card()
                    card.number = (number + 1)
                    card.suit = suit
                    card.deck = deck
                    card.save()

                # Add special suits
                jack = Card()
                jack.number = 11
                jack.suit = suit
                jack.deck = deck
                jack.save()

                queen = Card()
                queen.number = 12
                queen.suit = suit
                queen.deck = deck
                queen.save()

                king = Card()
                king.number = 13
                king.suit = suit
                king.deck = deck
                king.save()

            # Create jokers
            if joker:
                for joker_number in range(joker_count):
                    jokerCard = Card()
                    jokerCard.number = 99
                    jokerCard.suit = 99
                    jokerCard.deck = deck
                    jokerCard.save()
        
        return deck

SUITS = (
    (0,'Trebol'),
    (1,'Corazon'),
    (2,'Espada'),
    (3,'Diamante'),
    (99, 'Joker')
)
class Card(models.Model):
    # Card Location
    deck = models.ForeignKey('game.Deck', on_delete = models.CASCADE, null = True)
    hand = models.ForeignKey('game.Hand', on_delete = models.CASCADE, null = True)
    field = models.ForeignKey('game.PlayerField', on_delete = models.CASCADE, null = True)

    graveyard = models.ForeignKey('game.Graveyard', on_delete = models.CASCADE, null = True)
    graveyard_position = models.IntegerField(null = True, blank = True)

    # Card data
    number = models.IntegerField()
    suit = models.IntegerField(choices = SUITS)

    def get_location(self):
        if self.deck is not None:
            return "Mazo"
        elif self.hand is not None:
            return "En mano"
        elif self.field is not None:
            return "En campo"
        elif self.graveyard is not None:
            return "Cementerio"
        else:
            return "En el limbo"

    def get_image_filename(self):
        # get rank
        numero = self.number
        if self.number == 1:
            numero = "A"
        if self.number == 11:
            numero = "J"
        if self.number == 12:
            numero = "Q"
        if self.number == 13:
            numero = "K"
        if self.number == 99:
            numero = "J"
        
        # get suit
        if self.suit == 0:
            letra = "C"
        if self.suit == 1:
            letra = "H"
        if self.suit == 2:
            letra = "S"
        if self.suit == 3:
            letra = "D"
        if self.suit == 99:
            letra = "J"
        
        return "{}{}.png".format(numero, letra)

    def __str__(self):
        return "[{}] {} ({})".format(self.get_suit_display(), self.number, self.get_location())
