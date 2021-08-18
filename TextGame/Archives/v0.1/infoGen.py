'''
Character Generation v0.1

Christian Carter

Creates a class for character generation
'''

import os

class Character:
    
    description = 'Sample text to be changed by user'
    
    def __init__(self, age, sex, gender, temperment, relationship_status):
        
        self.age = age
        self.sex = sex
        self.gender = gender
        self.temp = temperment
        self.r_status = relationship_status

    def birthday(self):
        self.age += 1

class Station:

    crew = []
    
    def __init__(self, food_amount = 0, water_amount = 0, tempurature = 0, morale = 0, weather = 'Sunny'):
        self.checkfood = food_amount
        self.checkwater = water_amount
        self.checktemp = tempurature
        self.checkmorale = morale
        self.checkweather = weather

    def addCrew(self, character_name):
        self.crew.append(character_name)

    def removeCrew(self, character_name):
        self.crew.remove(character_name)