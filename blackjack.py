#!/usr/bin/env python
# encoding: utf-8
"""
untitled.py

Created by James on 2014-07-03.
Copyright (c) 2014 __MyCompanyName__. All rights reserved.
"""
#to do:
## 1- Show the dealer's card
## 2- fix gameplay presentation/prompts
## 3- Allow for double?
## 4- fix the '52' number in the probablity function


import sys
import os
import random


deck = None
stats = {'player':{'win':0,'lose':0,'tie':0,'blackjack':0},'dealer':{'win':0,'lose':0,'tie':0,'blackjack':0}}
history = {'bets':[]}




def NewBlackjackGame():
	global stats
	player = Player()
	dealer = Player()
	game = Game(player, dealer,[])
	while player.credits > 1:
		game.play_round()
		print('Stats: '+str(stats['player']))
	if player.credits < 1:
		print('You are out of credits. Game over.')
		
class Hand():
	def __init__(self, owner):
		self.owner = owner
		self.cards =[]
		self.total = 0

	def show_hand(self):
		if self.owner == "player":
			print(self.owner + ' current hand: ' + str(self.cards) + ' for a total of: ' + str(self.total))
		#if self.owner == "dealer":
		#	print('Dealer shows :' + self.cards[0])

	def draw_card(self):
		global deck
		new_card = deck.draw()
		self.cards.append(new_card)
		print(self.owner + ' drew a ' + new_card)
		self.total = self.total + deck.values_lookup[new_card]
		#automatically take care of the "soft" "hard" business
		if "A" in self.cards and self.total + 10 <=21:
			self.total = self.total + 10
			print("Soft hand")
		if "A" in self.cards and self.total > 21 and self.total - 10 <=21:
			self.total = self.total - 10
			print("Hard hand")

	def clear_hand(self):
		del self.cards[:]
		self.total=0

class Game():
	def __init__(self, player, dealer, stats):
		self.player = player
		self.dealer = dealer
		self.stats = stats
		
	def hit_or_stand(self):
		choice = raw_input('Continue or stop? You have a ' + str(self.get_bust_probability(self.player.hand,self.dealer.hand)) + ' percent probability of busting')
		if choice == "q":
			return 0
		else:
			return 1
	def increment_stats(self,player,cat):
		global stats
		if player == 'player' and cat == 'win':
			stats['player']['win'] = stats['player']['win'] +1
			stats['dealer']['lose'] = stats['dealer']['lose'] +1
		if player == 'player' and cat == 'lose':
			stats['player']['lose'] = stats['player']['lose'] +1
			stats['dealer']['win'] = stats['dealer']['win'] +1
		if player == 'player' and cat == 'blackjack':
			stats['player']['blackjack'] = stats['player']['blackjack'] +1
			stats['dealer']['lose'] = stats['dealer']['lose'] +1
		if player=='dealer' and cat == 'blackjack':
			stats['player']['lose'] = stats['player']['lose'] +1
			stats['dealer']['blackjack'] = stats['dealer']['blackjack'] +1
			
	def play_round(self):
		global deck
		global history
		deck = Deck()
		deck.shuffle()
		self.player.hand.clear_hand()
		self.dealer.hand.clear_hand()
		initial_bet = 0
		##player turn##
		while initial_bet < 1 or initial_bet > self.player.credits:
			try:
				initial_bet = int(raw_input('How much would you like to bet? You have ' + str(self.player.credits) + ' credits. '))
				if initial_bet < 1:
					print('Please bet at least 1 credit')
				if initial_bet > self.player.credits:
					print('You do not have sufficent credits to make this wager. You have ' + str(self.player.credits) + ' credits left.')
			except ValueError:
				print('That was an invalide number. Please enter a value >= 1')
				
		print('You bet ' + str(initial_bet))
		self.player.change_credits(-initial_bet)
		history['bets'].append(initial_bet)
		
		for i in range(2):
			self.player.hand.draw_card()
			self.dealer.hand.draw_card()
		self.player.hand.show_hand()
		if self.player.hand.total <  21:
			hit = self.hit_or_stand()
		if self.player.hand.total == 21:
			print('Player Blackjack!')
			self.increment_stats('player', 'blackjack')
			self.player.change_credits(initial_bet*2.5) #3:2 retunrs for blackjack
			
		while self.player.hand.total < 21 and hit:
			self.player.hand.draw_card()
			self.player.hand.show_hand()
			if self.player.hand.total > 21:
				print('Player bust!')
				self.increment_stats('player', 'lose')
				break
			# if self.player.hand.total == 21 and len(self.player.hand.cards) == 2:
			# 			print('Player Blackjack!')
			# 			self.increment_stats('player', 'blackjack')
			# 			self.player.change_credits(initial_bet*2.5) #3:2 retunrs for blackjack
			# 			break
			#should I check for 21 with multiple cards?
			#if self.player.hand.total == 21 and len(self.player.hand.cards) > 2:
				
			hit = self.hit_or_stand()
			if hit == 0:
				break
		#player stands
		if hit == 0: 
			print('Player stands. Dealer turn')
			if self.dealer.hand.total > 17 and self.dealer.hand.total > self.player.hand.total:
				self.dealer.hand.show_hand()
				print('Dealer wins!')
				self.increment_stats('player', 'lose')
			while self.dealer.hand.total < 17:
				self.dealer.hand.draw_card()
				if self.dealer.hand.total >=17 and self.dealer.hand.total < 21:
					if self.dealer.hand.total > self.player.hand.total:
						print('Dealer wins!')
						self.increment_stats('player', 'lose')
						break
					else:
						#make this smarter...
						self.dealer.hand.draw_card()
				if self.dealer.hand.total > 21:
					print('Dealer bust. Player wins!')
					self.player.change_credits(2*int(initial_bet))
					self.increment_stats('player', 'win')
					
				if self.dealer.hand.total == 21:
					print('Dealer Blackjack!')
					self.increment_stats('dealer', 'blackjack')
					break
		print('Your current credit is: ' + str(self.player.credits))
			 	
	def get_bust_probability(self,player_hand,dealer_hand):
		#we need a new deck to get the proper counts
		global deck
		margin = 21 - player_hand.total
		deck.card_values.append(deck.values_lookup[dealer_hand.cards[1]]) #we need to put back the dealer's hidden card since we cannot account for it in the probabilities
		over_margin = len([c for c in deck.card_values if c > margin]) 
		deck.card_values.remove(deck.values_lookup[dealer_hand.cards[1]]) #remove the dealer's hidden card that we had inserted to compute accurate probabilities
		return round((over_margin/52.0)*100.0)
	
class Deck():
	def __init__(self):
		self.values_lookup = {'A':1,'2':2,'3':3,'4':4, '5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'K':10,'Q':10}
		self.cards = list(self.values_lookup.keys())*4
		self.card_values = list(self.values_lookup.values())*4
		
	def shuffle(self):
		random.shuffle(self.cards)
				
	def draw(self):
		self.card_values.remove(self.values_lookup[self.cards[0]]) #update the values list
		return self.cards.pop(0)
	
	def cards_left(self):
		return len(self.cards)

class Player():
	def __init__(self):
		self.credits = 100
		self.hand = Hand("player")
	
	def get_credits(self):
		return self.credits
		
	def change_credits(self,value):
		self.credits = self.credits + value
		

		

def main():
	NewBlackjackGame()

if __name__ == '__main__':
	main()

