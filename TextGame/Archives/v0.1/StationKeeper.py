from sys import version_info


version_info = "v0.1"
import os
import time
os.system ('cls')
print ("Welcome to Station Keeper v0.1")
time.sleep(1)
os.system ('cls')
print ("Please enter your name")
print (" ")
name = input ("")
time.sleep(1)
os.system('cls')
print (f"Hello, {name}")
time.sleep(2)
os.system('cls')

def Antarctica():
    pause = " "
    food = 83
    water = 74
    heat = 78
    morale = 100
    weather = 0
    hour = 7
    minute = 37
    os.system('cls')
    print (f"Food: {food}")
    time.sleep(2)
    print (f"Water: {water}")
    time.sleep(2)
    print (f"Temp: {heat}")
    time.sleep(2)
    print (f"Morale: {morale}")
    time.sleep(2)
    print ("Weather; 0:Clear, 1:Snowing, 2:Storm")
    print (f"Weather: {weather}")
    time.sleep(2)
    print (f"Time: {hour}:{minute}")
    while pause == " ":
        time.sleep(3)
        minute = minute + 1
        print (f"Time: {hour}:{minute}")
        
        if minute == 60:
            hour = hour + 1
            minute = 0
            print (f"Time: {hour}:{minute}")
            continue





def AntarcticaMain():
    os.system('cls')
    print ("Welcome to Antarctica")
    time.sleep(2)
    print ("You have been tasked with keeping your crew alive.")
    time.sleep(2)
    print ("You must manage things in a sustainable way in order to survive.")
    time.sleep(2)
    os.system('cls')
    print ("GOOD LUCK!")
    time.sleep(2)
    os.system('cls')
    Antarctica()

def main():
    choice = '0'
    while choice == '0':
        print ("Which station would you like to tend:")
        print ("Antarctica")
        choice = input (' ')

        if choice == "Antarctica":
            os.system ('cls')
            print ("Heading to Antarctica...")
            time.sleep(2)
            AntarcticaMain()
        break

main()
