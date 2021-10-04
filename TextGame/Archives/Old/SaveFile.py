'''
Save File v0.1

Christian Carter

Save file api
'''
import os

def createSave(save_name):
    '''
    (str) -> None

    Creates a new save file named with save_name if one hasn't been made
    returns False and ends the program if the name has been taken
    '''  
    save_files = readSaveFiles('Saves')
    save_file_name = f'{save_name}.txt'
    for name in save_files:
        if save_file_name == name:
            success_state = False
            return success_state   
    new_save = open(f'{save_file_name}', 'w+')
    save_str = 'Stations = []\n'
    new_save.write(f'save_name = {save_name}' + f'\nsave_string = \n{save_str}')
    new_save.close()
    os.rename(save_file_name, f'Saves/{save_file_name}')
    success_state = True
        
    return success_state

def readSaveFiles(dir):
    '''
    () -> list

    Reads the save file folder and returns a list of the file names
    '''
    directory = os.scandir(f'{dir}')
    saves = []
    for item in directory:
        saves.append(item.name)
    return saves

def writeSaveStr():
    pass

def openSave():
    pass
