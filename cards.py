#!/usr/bin/env python
# encoding: utf-8

from random import *
import glob
import json
import html

folder = 'FixedDecks/'
filename = '*.json'

#folder = ''
#filename = 'a.json'

files = glob.glob(folder + filename)
replaces = {
    '<i>':'',
    '</i>':'',
    '<b>':'',
    '</b>':'',
    '<br>':' ',
    '<br/>':' '}


class Cards():
    def __init__(self):
        self.blackCards = {}
        self.whiteCards = []
        self.collectBlackCards()
        self.collectWhiteCards()
    
    def collectBlackCards(self):
        for f in files:
            data = open(f)
            raw = json.load(data)
            data.close()
            for card in raw['blackCards']:
                card['text'] = html.unescape(card['text'])
                for key in replaces:
                    card['text'] = card['text'].replace(key, replaces[key])
                
                try:
                    try:
                        card = card.encode('latin1')
                    except:
                        card = card.encode('utf-8')
                except:
                    pass

                if card['pick'] not in self.blackCards:
                    self.blackCards[card['pick']] = []
                if card not in self.blackCards[card['pick']]:
                    self.blackCards[card['pick']].append(card)
        for pick in self.blackCards:
            shuffle(self.blackCards[pick])
        print('black picks', len(self.blackCards))
        s = 0
        for pick in self.blackCards:
            s += len(self.blackCards[pick])
        print('black', s)
    
    def collectWhiteCards(self):
        for f in files:
            data = open(f)
            raw = json.load(data)
            data.close()
            for card in raw['whiteCards']:
                card = html.unescape(card)
                for key in replaces:
                    card = card.replace(key, replaces[key])
                    
                try:
                    try:
                        card = card.encode('latin1')
                    except:
                        card = card.encode('utf-8')
                except:
                    pass
                    
                if card not in self.whiteCards:
                    self.whiteCards.append(card)
        shuffle(self.whiteCards)
        print('white', len(self.whiteCards))

    def getRandomBlack(self, l):
        if l == -1:
            l = choice(list(self.blackCards.keys()))
        if not self.blackCards[l]:
            self.collectBlackCards()
        card = self.blackCards[l].pop()
        return card

    def getRandomWhite(self):
        if not self.whiteCards:
            self.collectWhiteCards()
        card = self.whiteCards.pop()
        return card.decode("utf-8")

    def isAcceptableLength(self, l):
        return l in self.blackCards


# Inserting text from white cards into black card
def insertWhiteInBlack(black, white):
    if '____' not in black:
        black += '  ____.' * len(white)
    for card in white:
        card = '_' + card + '_'
        card = card.replace('._', '_')
        black = black.replace('____', card, 1)
    black = black.replace('____', white[-1])
    black = black.replace('  ', ' ')
    return black
