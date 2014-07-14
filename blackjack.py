#!/usr/bin/env python
# encoding: utf-8
"""
blackjack.py

Created by James on 2014-07-03.
"""


import sys
import os
import random


#credits not updating properly

class Analytics():
	"""Analyze playing patterns and probabilities"""
	def __init__(self,player,dealer,deck):
			self.player = player
			self.dealer = dealer
			self.deck =deck
	def get_bust_probability():
		margin = 21 - self.player.hand.total
		self.deck.cards.append(self.dealer.hand.cards[1]) #we need to put back the dealer's hidden card since we cannot account for it in the probabilities
		over_margin = len([c for c in self.deck.cards if c.value > margin]) 
		self.deck.cards.remove(self.dealer.hand.cards[1]) #remove the dealer's hidden card that we had inserted to compute accurate probabilities
		return round((over_margin/len(Deck().cards))*100.0)
	
class Game():
	
	def __init__(self, player,start_credit = 100):
		"""Initializes a new game with one player and dealer. Start credits = 100"""
		self.dealer = Dealer()
		self.deck = Deck()
		self.player = Player(player,start_credit)
		
	def get_player_bet(self):
		"""Prompt the player to make bet. Bet must be $1 or greater and cannot exceed current balance."""
		initial_bet = 0
		while initial_bet < 1 or initial_bet > self.player.credits:
			try:
				initial_bet = int(raw_input('How much would you like to bet? You have ' + str(self.player.credits) + ' credits. '))
				if initial_bet < 1:
					print('Please bet at least 1 credit')
				if initial_bet > self.player.credits:
					print('You do not have sufficient credits to make this wager. You have ' + str(self.player.credits) + ' credits left.')
			except ValueError:
				print('That was an invalid number. Please enter a value >= 1')
		self.player.bet = initial_bet
		return initial_bet
	
	def deal_cards(self):
		"""Randomly serve two cards to player and dealer"""
		for i in range(2):
			self.player.hand.draw_from_deck(self.deck)
			self.dealer.hand.draw_from_deck(self.deck)
			
	def check_for_blackjack(self):
		"""Verifies if the player or dealer got a blackjack at the beginning of the round. Returns 1,0,-1 for a win, tie, and loss respectively. Otherwise returns None"""
		winner = None
		blackjack = False
		if self.player.hand.total == 21 and len(self.player.hand.cards)==2:
			if self.dealer.hand.total == 21 and len(self.dealer.hand.cards)==2:
				print('Push!')
				winner = 0
			else:
				print(self.player.name+' blackjack!')
				winner = 1
				blackjack = True
		if self.dealer.hand.total == 21 and len(self.dealer.hand.cards)==2:
			self.dealer.show_hand(True)
			print("Dealer blackjack!")
			winner = -1
		return (winner,blackjack)
		
	def check_for_bust(self,player):
		"""See if a hand's total exceeds 21"""
		bust = False
		if player.hand.total > 21:
			bust = True
		return bust
	
	def get_winner(self):
		"""Pick the winner based on hand totals returns 1, 0, -1, for player wins, tie, and dealer wins respectively"""
		if self.check_for_bust(self.dealer):
			print('Dealer bust')
			return 1
		if self.dealer.hand.total >= 17 and self.dealer.hand.total > self.player.hand.total:
			print('Dealer wins')
			return -1
		if self.dealer.hand.total < self.player.hand.total:
			print(self.player.name + (' wins!'))
			return 1
		if self.dealer.hand.total == self.player.hand.total:
			print('Push!')
			return 0
		
	def deal_two_cards_each(self,dealer_turn):
		"""Pick two random cards for both player and dealer and display them."""
		self.deal_cards()
		self.player.show_hand()
		self.dealer.show_hand(dealer_turn)
		
	def play_one_round(self):
		""" Play a single hand. Both player and dealer take turns after drawing two cards from the deck."""
		blackjack = False
		self.player.bet = self.get_player_bet()
		self.player.credits  = self.player.credits-self.player.bet #remove the bet amount from the player's account
		print('You bet ' + str(self.player.bet))
		dealer_turn = False
		self.deal_two_cards_each(dealer_turn)
		winner,is_blackjack = self.check_for_blackjack() #check to see if anyone got a blackjack outright
		if not winner == None:
			self.update_credits(winner, is_blackjack)
		if winner == None:
			self.player.play_hand(self.deck,self.dealer)
			if self.check_for_bust(self.player):
				print('Player bust!')
				winner =  -1
		if winner == None:
			print('Player stands. Dealer turn')
			dealer_turn = True
			self.dealer.show_hand(dealer_turn)
			self.dealer.play_hand(self.deck,dealer_turn,self.player)
			winner =  self.get_winner()
			self.update_credits(winner, is_blackjack)
		assert not winner == None #if there is no winner at this stage something is wrong!
		self.player.hand.return_to_deck(self.deck)
		self.dealer.hand.return_to_deck(self.deck)
		
	def update_credits(self,winner,is_blackjack):
		"""Credit the player's account if they win or tie"""
		if winner == 1 and is_blackjack:
			self.player.credits = self.player.credits + (2.5 * self.player.bet)
		if winner == 1 and (not is_blackjack):
			self.player.credits = self.player.credits + (2 * self.player.bet)
		if winner == 0:
			self.player.credits = self.player.credits + self.player.bet
		
	def start(self):
		"""This is where the game flow is controlled."""
		round_number = 1
		while self.player.credits >= 1:
			self.deck.shuffle()
			print('### Round '+str(round_number)+' ###')
			winner = self.play_one_round()
			self.record_player_history(winner)
			round_number = round_number+1
			print self.player.history['moves']
			print self.player.history['bets']
			
	def record_player_history(self,winner):
		self.player.history['outcome'].append(winner)
		self.player.history['bets'].append(self.player.bet)
		self.player.history['rounds'] = self.player.history['rounds'] + 1
	
class Dealer():
	def __init__(self):
		"""Initialize a new Dealer with an empty hand"""
		self.hand = Hand()
	
	def show_hand(self, dealer_turn):
		"""Prints the dealer's hand and only shows a single card if it's no the dealer's turn"""
		if dealer_turn:
			print('Dealer current hand: ')
			for c in self.hand.cards:
				print(c)
			print('For a total of: ' + str(self.hand.total))
		else:
			print('Dealer shows: ' + str(self.hand.cards[0]) + ' and <card face down>') #don't show the card in the hole
		
	def play_hand(self, deck, dealer_turn, player):
		"""The dealer playing logic. Keep hitting until above 17. Hit also if you have a soft 17 e.g. 17 with Ace."""
		while self.hand.total < 17 or (self.hand.total == 17 and any(c.face == 'Ace' for c in self.hand.cards)):
				print('Dealer draws card...')
				self.hand.draw_from_deck(deck)
				self.show_hand(dealer_turn)
		

class Deck():
	"""A standard 52-card deck."""
	SUITS = ['Spades', 'Hearts','Clubs', 'Diamonds']
	FACES = ['Ace','King','Queen','Jack']
	def __init__(self):
		"""Create a deck with all suits and values."""
		self.cards=[]
		for s in self.SUITS:
			for val in range(9):
				self.cards.append(Card(val+2,s))
			for f in self.FACES:
				self.cards.append(Card(f,s))
						
	def shuffle(self):
		"""Randomly shuffle the deck."""
		random.shuffle(self.cards)
				
	def next_card(self):
		"""Return the card on top of the deck."""
		return self.cards.pop(0)
	

class Player():
	"""A class to handle player logic such as available credits and game decisions"""
	def __init__(self, name, credits):
		"""Initialize a new player and record its moves"""
		self.credits = credits
		self.name = name
		self.hand = Hand()
		self.bet = 0
		self.help = False
		self.move_number = 0
		self.history = {'rounds':0,'bets':[], 'outcome':[], 'moves':[]} #use later to log playing history
	def show_hand(self):
		"""Print the value of the player's hand."""
		print(self.name + ' current hand: ')
		for c in self.hand.cards:
			print(c) 
		print('For a total of: ' + str(self.hand.total))
	def play_hand(self,deck, dealer):
		"""Controls the player logic to hit, stand, or double down. Returns player choice to handle case with double dowm"""
		hit = 1
		self.help = True
		while self.hand.total < 21 and hit == 1:
			hit = self.hit_or_stand(self.help,deck,dealer)
			self.move_number = self.move_number + 1
			if not hit == 1:
				break
			self.hand.draw_from_deck(deck)
			self.show_hand()
		if hit == 2:
			self.credits = self.credits - self.bet #remove the additional wager from player account
			self.bet = self.bet * 2 #update the bet field to reflect double down
			print(self.name + " doubles down. Total wager: " + str(self.bet))
			self.hand.draw_from_deck(deck)
			self.show_hand()
			return 
		if hit == 0 or self.hand.total >= 21:
			return 
	
	def get_bust_probability(self,deck,dealer):
		margin = 21 - self.hand.total
		deck.cards.append(dealer.hand.cards[1]) #we need to put back the dealer's hidden card since we cannot account for it in the probabilities
		over_margin = len([c for c in deck.cards if c.value > margin]) * 1.0
		deck.cards.remove(dealer.hand.cards[1]) #remove the dealer's hidden card that we had inserted to compute accurate probabilities
		return round((over_margin/len(Deck().cards))*100.0) #in case there is more than a single deck
	
	def hit_or_stand(self, help,deck,dealer):
		"""Prompt the player to hit, stand, or double her wager. Give bust probabilities if the player asked for help"""
		risk = self.get_bust_probability(deck, dealer)
		move = 1 #assume the player hits
		if len(self.hand.cards)==2:
			if not help:
				choice = raw_input('Press any key to Hit, "s" to [s]tand, or "d" to [d]ouble down > ')
			else:
				choice = raw_input('Press any key to Hit, "s" to [s]tand, or "d" to [d]ouble down. You have a ' + str(risk) + ' percent probability of busting >')
		else:#if your have more than two cards you can't double down
			if not help:
				choice = raw_input('Press any key to Hit or "s" to [s]tand > ')
			else:
				choice = raw_input('Press any key to Hit or "s" to [s]tand. You have a ' + str(risk) + ' percent probability of busting >')
		if choice == "s":
			move = 0
		if choice == "d" and len(self.hand.cards)==2:
			move =  2
		self.log_move_and_risk(move,risk)
		return move
	
	def log_move_and_risk(self,move,risk):
		self.history['moves'].append({self.move_number:[move,risk]})
		
class Card():
	"""A class to handle card logic"""
	FACES = {'Ace':1,'Jack':10,'King':10,'Queen':10}
	def __init__(self,face,suit):
		"""initialize a Card object with a face and suit e.g. Card(Ace,Spades)"""	
		self.face = face
		self.suit = suit
	def __str__(self):
		"""string representation of a Card e.g. Ace of Spades"""
		return "{0.face} of {0.suit}".format(self)
	@property
	def value(self):
		"""Return the face value of a card e.g. 7"""
		return self.FACES.get(self.face,self.face)			

class Hand():
	"""A list of Card objects"""
	def __init__(self):
		"""Initializes an empty list of Card objects"""
		self.cards =[]
		
	def draw_from_deck(self,deck):
		"""Draws the card on top of the deck."""
		self.cards.append(deck.next_card())
		
	def return_to_deck(self,deck):
		"""Clears the hand and places the cards in hand back into the deck."""
		for c in self.cards:
			deck.cards.append(c)
		del self.cards[:]
			
	@property
	def total(self):
		"""Returns the total value of the cards in the hand. It also checks if there is an Ace to handle soft vs. hard."""
		if any(c.face == 'Ace' for c in self.cards):
			total_of_non_ace_cards = sum(c.value for c in self.cards if c.face != 'Ace')
			if total_of_non_ace_cards <= 10:
				for i in range(len(self.cards)):
					if self.cards[i].face == 'Ace':
						self.cards[i].value = 11
						break
			else:
				for i in range(len(self.cards)):
					if self.cards[i].face == 'Ace' and self.cards[i].value==11:
						self.cards[i].value = 1
						break
			return sum(c.value for c in self.cards)  	
		else:
			return sum(c.value for c in self.cards)  

		

def main():
	g = Game("James",100)
	g.start()

if __name__ == '__main__':
	main()

