'''
Station Keeper v0.2

Christian Carter

Terminal based text game

Depreciated. Start-up code is now located in GameEngine.py
'''
version_info = "v0.2"
import time
import os
import sys
import SaveFile as save

version_info = 'v0.2'

def cls():
    '''
    clears the terminal
    '''
    os.system('cls')

def startUp():
    '''
    Prints the start up spalsh text
    '''
    buffer = '******************************' #30 *s
    game_info = 'Station Keeper ' + version_info

    print(buffer * 3)
    print(buffer + f'{game_info:^30}' + buffer)
    print(buffer * 3)
    return None

def homeScreen():
    '''
    Displays the home screen splash with new, load, and exit options
    '''
    buffer = '***'
    nle_str = '***  New *** Load *** Exit ***'
    menu_choice = ''
    is_valid_input = True
    while is_valid_input:
        cls()
        menu_choice = input(f'{buffer * 30}' + f'\n{buffer * 10}' + f'{nle_str}' + f'{buffer * 10}' + f'\n{buffer * 30}\n').lower()
        if menu_choice == 'new' or menu_choice == 'load' or menu_choice == 'exit':
            is_valid_input = False

    if menu_choice == 'new':
        cls()
        success = False
        while success == False:
            save_name = input('Enter the name of your save: ')
            success_attempt = save.createSave(save_name)
            if success_attempt:
                success = True
            else:
                cls()
                print('Save name already taken. Please choose another name.')
                time.sleep(2)
                cls()


    if menu_choice == 'load':
        loadScreen()

    if menu_choice == 'exit':
        sys.exit()
    
    return None

def loadScreen():
    '''
    () -> str

    Fetches the save file names and prints them, asking the user to input a valid save file name
    Returns a valid save file selection
    '''
    
    saves = save.readSaveFiles('Saves')
    entry_bool = False
    while entry_bool == False:
        cls()
        print('Enter a valid save file name: ')
        for entry in saves:
            print(entry[:-4])
        save_choice = input('\n')
        for entry in saves:
            if save_choice == entry[:-4]:
                entry_bool = True
                break
            else: 
                entry_bool = False
    cls()
    print(f'Loading {save_choice}...')
    return save_choice
    
    
def initialize():
    
    cls()
    startUp()
    time.sleep(2)
    cls()
    homeScreen()
    
    return None

def main():
    initialize()
    return None

main()