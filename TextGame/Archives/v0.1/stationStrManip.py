'''
Station String Manipulation v0.1

Christian Carter

Creates and manipulates strings for the easy generation of stations without manually having to input everything
'''

import os
import sys
import infoGen
from SaveFile import readSaveFiles 

def createStationString(station_name):
    '''
    () -> bool

    Creates a file and populates it with information blanks i.e., Name = \nFood = \n
    '''
    save_name = f'{station_name}.txt'
    saves = readSaveFiles('stationStrings')
    for file in saves:
        if save_name == file:
            sys.exit()
    info_blanks = ['station_name = ', 'food_amount = ', 'water_amount = ', 'tempurature = ', 'morale = ', 'weather = ', 'crew = ']
    file = open(save_name, 'w')
    for line in info_blanks:
        file.writelines(line)
    file.close()
    os.rename(save_name, f'stationStrings/{save_name}')

def readStationString(station_name, save_name):
    '''
    (str) ->

    Creates stations based on station strings
    '''
    info_list = {}
    file = open(f'stationStrings/{station_name}.txt', 'r')
    new_file = open(f'Saves/stations/{save_name}{station_name}.txt', 'w+')
    for line in file:
        new_file.writelines(line)
        new_line = line.split()
        info_list[new_line[0]] = new_line[-1]
    
    globals()[info_list['station_name']] = infoGen.Station( info_list['food_amount'], 
                                                            info_list['water_amount'], 
                                                            info_list['tempurature'],
                                                            info_list['morale'],
                                                            info_list['weather'])
    
