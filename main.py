#!/usr/bin/python

#     __                           _   _                                       
#    /__\__  ___ __ _ _ __   ___  | |_| |__   ___    /\  /\___  _   _ ___  ___ 
#   /_\/ __|/ __/ _` | '_ \ / _ \ | __| '_ \ / _ \  / /_/ / _ \| | | / __|/ _ \
#  //__\__ \ (_| (_| | |_) |  __/ | |_| | | |  __/ / __  / (_) | |_| \__ \  __/
#  \__/|___/\___\__,_| .__/ \___|  \__|_| |_|\___| \/ /_/ \___/ \__,_|___/\___|
#                  |_|                                                          

# Modified By Sam Scotford
# Credits to Al Sweigart for bulk of sorce code 
# - https://inventwithpython.com/blog/2014/12/11/making-a-text-adventure-game-with-the-cmd-and-textwrap-python-modules/
#
# To-Do:
#   Have a lighting system like in Zork, where the player must have a torch to enter certain rooms
#   Have some combat
#   Items within items needs fixing / implementing
#   Fix bug where trying to store items outside of the mainhall produces an error
#   Ui Improvements


import _random
import datetime
#import player_class # Player class external
import os
import cmd
import textwrap
import colorama
import ctypes
import platform

# Output colors

colorama.init()

# Set Window title
#ctypes.windll.kernel32.SetConsoleTitleA("Escape The House v5.0.9")

class bcolors:
    start = "\033[1;31m"
    end = "\033[0;0m"

# Constent variables
DEFAULT = ''
DESC = 'desc'
NORTH = 'north'
SOUTH = 'south'
EAST = 'east'
WEST = 'west'
UP = 'up'
DOWN = 'down'
GROUND = 'ground'
STORAGE = 'storage'
DOOR = 'door'
HIDDEN = 'hidden'
GROUNDDESC = 'grounddesc'
INVDESC = 'invdesc'
SHORTDESC = 'shortdesc'
LONGDESC = 'longdesc'
TAKEABLE = 'takeable'
STORABLE = 'storeable' # able to be stored in a bag / items inventory
STORAGE = 'storage'
STORAGEDESC = 'storagedesc'
EDIBLE = 'edible'
USEABLE = 'usable'
TOGGLE = 'TOGGLE'
USEDESCTRUE = 'usedesctrue'
USEDESCFALSE = 'usedescfalse'
ITEMINV = 'iteminv'
ITEM_INVENTORY = []
DESCWORDS = 'descwords'
SCREEN_WIDTH = 80
location = 'Entrance Hall' # Start here
inventory = ['Personal ID']
showFullExits = False

# Define rooms here

worldRooms = {
        'Entrance Hall': {
                DESC: "You stand in a hallway with a single door infront of you, the room is dimly lit from a single bulb that flickers occosionally.",
                NORTH: 'Main Hall',
                GROUND: ['Old Key', 'Note', 'Sack'],
            },
        'Main Hall': {
                DESC: 'You stand in the main hall there are debris everywhere you look it looks a bomb went off in here, there is also a small troll statue on the side table.',
                SOUTH: 'Entrance Hall',
                EAST: 'Kitchen',
                WEST: 'Library',
                UP: '2nd Floor',
                GROUND: ['Torch', 'Chest', 'Troll'],
                STORAGE: [], # Used to store items and win the game
            },
            
        'Kitchen' : {
                DESC: "You stand in what appears to be a large kitchen, pots and pans hang from the walls and though dusty look quite well used.",
                SOUTH: 'Main Hall',
                EAST: 'Garden',
                GROUND: '',
        },
        
        'Garden' : {
            DESC: "You are in an overgrown garden, a prestine lawn-mower lies in the undergrown somewhat ironically, a tree house can be seen in the distance",
            WEST: "Kitchen",
            UP: "Treehouse",
            GROUND: '',
        },
        
        "Treehouse" : {
            DESC: "With much effort on your part and that of the rather brittle ladders, you make it to the top, a strong breeze shakes the tree and you being to feel rather ill.",
            NORTH: "Flimsy Branch",
            DOWN: "Garden",
            GROUND: "",

        },
            
        'Library': {
                DESC: "You walk into the Library, the smell of dusty books invades your nostrils. There is a valuted ceiling here and the moonlight shines into the room through stained glass windows making dancing shapes on the bookcases.",
                EAST: 'Main Hall',
                GROUND: ['Dusty Books', 'Gun'],
            },

        'Library 2nd Floor': {
                DESC : "You pass thorugh a creaky door on your way to the second floor libary.",
                EAST : "2nd Floor",
                GROUND : "",
        },
        
        '2nd Floor' : {
                DESC: "You go up the spiraling staircase onto the second floor, the first was blocked by an impassable door, you look down and have sudden virtigo from the height, you turn around.",
                DOWN: 'Main Hall',
                WEST : 'Library 2nd Floor',
                EAST : 'Bedroom',
                UP : 'Attic',
                GROUND:['Cassette']
        },

        'Attic' : {
            DESC : "Above you is an old wooden hatch with a brass ring, using your feeble legs you give up trying to reach for it and instead grab a hook from beside you and leaver the creaky door open, about a million weevels fall from the opening. You climb inside.",
            DOWN : "2nd Floor",
            UP: "Roof",
            GROUND : ['Weevels']
        }
        
    }

# Define items in the world

worldItems = {
        'Old Key': {
                GROUNDDESC: 'A dull brass key lies on the ground here.',
                SHORTDESC: 'Old key',
                LONGDESC: 'The old key has intricate inscriptions on it, it is covered in dust from years of unuse, it is cool to the touch.',
                TAKEABLE: True,
                EDIBLE: False,
                USEABLE: True,
                DESCWORDS: ['old', 'key'],
                STORAGEDESC: '[The old key] is within the chest, its like leaving the car keys in the in the car and regretting ever being born, good job..'
                

            },
        'Personal ID': {
                GROUNDDESC: 'Your personal identification card lies on the floor.',
                SHORTDESC: 'Your ID card.',
                LONGDESC: 'Through much mental anguish you read your card, You are Henry Burton, your age is 34 and have no idea of where you are.',
                TAKEABLE: True,
                DESCWORDS: ['id', 'card'],
                EDIBLE: False,
                USEABLE: False,
                STORAGEDESC: '[ID] Not even the blackness of the chest can hide your ugly mug, not even the weevles will go near it.',
            },
        'Note': {
                GROUNDDESC: 'A note lies here, its hard to make out what it says from where you are',
                SHORTDESC: 'Note',
                LONGDESC: 'Its a note and it reads "There was no mailbox outside to leave this in so I just left it here.."',
                TAKEABLE: True,
                EDIBLE: True,
                USEABLE: True,
                USEDESCTRUE: 'You use the note, and wipe your snotty nose with it, now you have a snotty note, gross.',
                DESCWORDS: ['note'],
                STORAGEDESC : '[Note] Not sure when you want this in here, but it is regardless..'
                
            },
        'Torch': {
                GROUNDDESC: 'A typical torch / flashlight lies on the floor',
                SHORTDESC: 'Torch / Flashlight.',
                LONGDESC: 'The torch / flashlight emits a soft flow, just enough to light the way.',
                EDIBLE: False,
                USEABLE: True,
                TOGGLE: False,
                USEDESCTRUE: 'You click the top of the touch, a beam illuminates your way, you can now be lost and see what you are doing.',
                USEDESCFALSE: 'YOu click the top of the touch, you think "Hey who turned out the lights.", the torch stays on, you bust the switch with your meaty fingers.. good job.',
                DESCWORDS: ['torch', 'flashlight'],
                STORAGEDESC: '[Torch] In the blackness of the chest not even the torches light esacpes.. spooky.',
            },
            
        'Dusty Books': {
            GROUNDDESC: 'A pile of dusty books lies on the floor near a reading desk.',
            SHORTDESC: 'Dusty Books',
            LONGDESC: 'A pile of dusty old books pages half rotting away, its hard to make out what is written in them, Hitchickers Guide to the Galaxy, How to stew a ham in 43 different ways and various other, written, human detritus.',
            EDIBLE: False,
            USEABLE: False,
            DESCWORDS: ['books','book'],
            STORAGEDESC: '[Dusty Books] The books lie at the bottom of the chest looking miserable.'
        },
        
        'Gun': {
            GROUNDDESC: 'A gun lies on the floor here.',
            SHORTDESC: 'Gun',
            LONGDESC: 'A 32 ACP revolver it has 5 chaimbers, one of the cartridges has been fired.',
            EDIBLE: False,
            USEABLE: True,
            DESCWORDS: ['Gun','gun','revolver'],
            STORAGEDESC: '[Gun] Better the gun be in here then in my hands..',
        },
        
        'Sack': {
            GROUNDDESC: 'A sack of burlap lies on the floor here',
            SHORTDESC: 'Sack',
            LONGDESC: 'Its an old sack used for storing things in, it smells like onions.',
            EDIBLE: False,
            DESCWORDS: ['Sack', 'bag', 'sack'],
            STORAGEDESC: '[Sack] A container with in a container, its like that terrible movie with Leonardo DiCaprio..',
            # Attempting "Items within Items"
            ITEMINV: ['Lunch'],
            
        },
        
        'Chest' : {
            SHORTDESC: 'A wooden chest',
            GROUNDDESC: 'A wooden chest resides in the far corner of this room with an incription on it.',
            LONGDESC: 'Its an old wooden chest with the inscription "Por viaj malmolaj gajnitaj eroj." the language begins with an Esp... you know that much.',
            EDIBLE: False,
            TAKEABLE: False,
            USEABLE: False,
            DESCWORDS: ['Chest', 'Box', 'Crate', 'chest', 'box', 'crate'],
        },
        
        'Troll' : {
            SHORTDESC: 'A troll figure',
            GROUNDDESC : 'A troll is somewhere around here.',
            LONGDESC : 'A small troll figure carved from wood, you turn it over in your hands, an inscription on the base "RIP Inbag the Troll.", a disembodied scottish voice tells you to not put it in your bag.',
            EDIBLE : False,
            USEABLE: False,
            TAKEABLE : False,
            DESCWORDS : ['Troll', 'troll', 'figure', 'statue'],
            STORAGEDESC : '[Troll] The troll lies disgruntled in the chest, its dark in there, it might be eaten by a Grew.'
        },
        
        'Cassette' : {
            SHORTDESC: 'A cassette tape',
            GROUNDDESC: 'A cassette tape lies here on the floor, someone must have "dropped the bass".',
            LONGDESC: 'You turn the cassette tape over in your hands, the lable reads "Best of the 60s", it possibly contains Fleetwood Mac and thus must be destroyed immediately.',
            EDIBLE: False,
            USEABLE: False,
            TAKEABLE: True,
            DESCWORDS: ['tape', 'cassette', 'music tape', 'music'],
            STORAGEDESC : '[Tape] A tape lies in the bottom of the chest, we would have prefered you to burn it but this choice is yours.',
        },

        'Weevels' : {
            SHORTDESC: 'A pile of dead weevels',
            GROUNDDESC : 'A pile of rotting weeveles lay on the ground.',
            LONGDESC : 'Its a pile of fucking rotting weevels',
            EDIBLE : True,
            USEABLE : False,
            TAKEABLE : True,
            DESCWORDS: ['weevels', 'pile of weevels', 'rotting weevels'],
            STORAGEDESC : '[Weevels] A pile of rotting weevel husks lie at the bottom of the chest.'
        }
    }

global default
default = ""

def displayLocation(loc, default):
    """A helper function for displaying an area's description and exits."""
    # Print the room name.
    print(bcolors.start + loc + bcolors.end)
    print('=' * len(loc))

    # Print the room's description (using textwrap.wrap())
    print('\n'.join(textwrap.wrap(worldRooms[loc][DESC], SCREEN_WIDTH)))

    # Print all the items on the ground.
    if len(worldRooms[loc][GROUND]) > 0:
        print("")
        for item in worldRooms[loc][GROUND]:
            print(worldItems[item][GROUNDDESC])
    
    try:
        # Check storage exists
        if len(worldRooms[loc][STORAGE]) > 0:
            print(bcolors.start + "The treasures you have accrewed thus far are (Chest) :" + bcolors.end)
            for item in worldRooms[loc][STORAGE]:
                print (worldItems[item][STORAGEDESC])
    except KeyError:
        return default
    
    
    # Print all the exits.
    exits = []
    for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
        if direction in worldRooms[loc].keys():
            exits.append(direction.title())
    print("")
    if showFullExits:
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction in worldRooms[location]:
                print('%s: %s' % (direction.title(), worldRooms[location][direction]))
    else:
        print('Exits: %s' % ' '.join(exits))


def moveDirection(direction):
    """A helper function that changes the location of the player."""
    global location

    if direction in worldRooms[location]:
        print('You move to the %s.' % direction)
        location = worldRooms[location][direction]
        displayLocation(location, default)
    else:
        print('You cannot move in that direction')


def getAllDescWords(itemList):
    """Returns a list of "description words" for each item named in itemList."""
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.extend(worldItems[item][DESCWORDS])
    return list(set(descWords))

def getAllFirstDescWords(itemList):
    """Returns a list of the first "description word" in the list of
    description words for each item named in itemList."""
    itemList = list(set(itemList)) # make itemList unique
    descWords = []
    for item in itemList:
        descWords.append(worldItems[item][DESCWORDS][0])
    return list(set(descWords))

def getFirstItemMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    for item in itemList:
        if desc in worldItems[item][DESCWORDS]:
            return item
    return None

def getAllItemsMatchingDesc(desc, itemList):
    itemList = list(set(itemList)) # make itemList unique
    matchingItems = []
    for item in itemList:
        if desc in worldItems[item][DESCWORDS]:
            matchingItems.append(item)
    return matchingItems

class TextAdventureCmd(cmd.Cmd):
    prompt = '\n> '
    # The default() method is called when none of the other do_*() command methods match.
    def default(self, arg):
        print('I do not understand that command. Type ' + bcolors.start + '"help"' + bcolors.end + ' for a list of commands.')

    # A very simple "quit" command to terminate the program:
    def do_quit(self, arg):
        """Quit the game."""
        return True # this exits the Cmd application loop in TextAdventureCmd.cmdloop()
    
    def help_combat(self):
        print('Combat is not implemented in this program.')

    # These direction commands have a long (i.e. north) and show (i.e. n) form.
    # Since the code is basically the same, I put it in the moveDirection()
    # function.
    def do_north(self, arg):
        """Go to the area to the north, if possible."""
        moveDirection('north')

    def do_south(self, arg):
        """Go to the area to the south, if possible."""
        moveDirection('south')

    def do_east(self, arg):
        """Go to the area to the east, if possible."""
        moveDirection('east')

    def do_west(self, arg):
        """Go to the area to the west, if possible."""
        moveDirection('west')

    def do_up(self, arg):
        """Go to the area upwards, if possible."""
        moveDirection('up')

    def do_down(self, arg):
        """Go to the area downwards, if possible."""
        moveDirection('down')

    # Since the code is the exact same, we can just copy the
    # methods with shortened names:
    do_n = do_north
    do_s = do_south
    do_e = do_east
    do_w = do_west
    do_u = do_up
    do_d = do_down

    def do_exits(self, arg):
        """Toggle showing full exit descriptions or brief exit descriptions."""
        global showFullExits
        showFullExits = not showFullExits
        if showFullExits:
            print('Showing full exit descriptions.')
        else:
            print('Showing brief exit descriptions.')
    
    
    
    def do_inventory(self, arg):
        """Display a list of the items in your possession."""

        if len(inventory) == 0:
            print('Inventory:\n  (nothing)')
            return

        # first get a count of each distinct item in the inventory
        itemCount = {}
        for item in inventory:
            if item in itemCount.keys():
                itemCount[item] += 1
            else:
                itemCount[item] = 1

        # get a list of inventory items with duplicates removed:
        print('Inventory:')
        for item in set(inventory):
            if itemCount[item] > 1:
                print('  %s (%s)' % (item, itemCount[item]))
            else:
                print('  ' + item)

    do_inv = do_inventory
    do_i = do_inventory

    def do_take(self, arg):
        """"take <item> - Take an item on the ground."""

        # put this value in a more suitably named variable
        itemToTake = arg.lower()

        if itemToTake == '':
            print('Take what? Type "look" the items on the ground here.')
            return
   

        cantTake = False

        # get the item name that the player's command describes
        for item in getAllItemsMatchingDesc(itemToTake, worldRooms[location][GROUND]):
            if worldItems[item].get(TAKEABLE, True) == False:
                cantTake = True
                continue # there may be other items named this that you can take, so we continue checking
            print("Taken.")
            worldRooms[location][GROUND].remove(item) # remove from the ground
            inventory.append(item) # add to inventory
            return
        
        # something funny
        if itemToTake == 'chest':
            print(bcolors.start + "Your feeble arms buckle under the weight of the enormous chest, nice try you theiving git." + bcolors.end)
            return
            
            
        if cantTake:
            print('You cannot take "%s".' % (itemToTake))
        else:
            print('That is not in or around the area, maybe it was your imagination?')
     
    

        
    
    def do_use(self, arg):
        """"use <item> - Use an item in in your inventory."""
        itemToUse = arg.lower()
        
        if itemToUse == '':
            print('Use what? Type "inv" to see the items in your invetory.')
            return
        
        cantUse = False
        
        #look up the item the player describes
        invDescWords = getAllDescWords(inventory)
        
        if itemToUse not in invDescWords:
            print('You do not have that item to use it')
            return
        
        for item in getAllItemsMatchingDesc(itemToUse, inventory):
            if worldItems[item].get(USEABLE, True) == False:
                cantUse = True
                continue
            print('%s' % (worldItems[item][USEDESCTRUE]))
            #print('You use %s' % (worldItems[item][SHORTDESC]))
            #inventory.remove(item) 
            return
        
        if cantUse:
            print('You cannot use "%s".' % (itemToUse))
        else:
            print('You do not have that item to use.')


    def do_drop(self, arg):
        """"drop <item> - Drop an item from your inventory onto the ground."""

        # put this value in a more suitably named variable
        itemToDrop = arg.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        # find out if the player doesn't have that item
        if itemToDrop not in invDescWords:
            print('You do not have "%s" in your inventory.' % (itemToDrop))
            return

        # get the item name that the player's command describes
        item = getFirstItemMatchingDesc(itemToDrop, inventory)
        if item != None:
            print('You drop %s.' % (worldItems[item][SHORTDESC]))
            inventory.remove(item) # remove from inventory
            worldRooms[location][GROUND].append(item) # add to the ground
    
    # put items in a item container
    def do_put(self, arg):
        """"put <item> in <item> - Puts an item in a container."""

        # put this value in a more suitably named variable
        itemToStore = arg.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)
        
        # Nice little easter egg :) 
        if itemToStore == 'troll in bag':
            print(bcolors.start + "You cannot put troll in bag, troll is a creature." + bcolors.end)
            return

        # find out if the player doesn't have that item
        if itemToStore not in invDescWords:
            print('You want to put "%s" in what?!' % (itemToStore))
            return
            

        # get the item name that the player's command describes
        item = getFirstItemMatchingDesc(itemToStore, inventory)
        if item != None:
            print('You put %s. in the container.' % (worldItems[item][SHORTDESC]))
            inventory.remove(item) # remove from inventory
            worldRooms[location][ITEMINV].append(item) # add to the container

    def do_store(self, arg):
        """"store <item> - Stores an item in a safe place, assuming that the room has a storage area."""

        # put this value in a more suitably named variable
        itemToStore = arg.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)
        
        # Nice little easter egg :) 
        if itemToStore == 'troll in bag':
            print(bcolors.start + "You cannot put troll in bag, troll is a creature." + bcolors.end)
            return

        # find out if the player doesn't have that item
        if itemToStore not in invDescWords:
            print('%s does not exist in your inventory, the ground, africa or your pockets, what a shame.' % (itemToStore))
            return
            

        # get the item name that the player's command describes
        
        try:
            item = getFirstItemMatchingDesc(itemToStore, inventory)
            
            # broken currently, needs some work doing to check if the STORAGE value exists in the current room then store the item.
            if item != None:
                print('You store %s in a safe place.' % (worldItems[item][SHORTDESC]))
                inventory.remove(item)
                worldRooms[location][STORAGE].append(item)
        except KeyError:
            return("Don't even think about it buster brown.")
        
        #item = getFirstItemMatchingDesc(itemToStore, inventory)
        #if item != None:
        #    print('You store %s in a safe place.' % (worldItems[item][SHORTDESC]))
        #    inventory.remove(item) # remove from inventory
        #    worldRooms[location][STORAGE].append(item) # add to the container
         
        
        

    def complete_take(self, text, line, begidx, endidx):
        possibleItems = []
        text = text.lower()

        # if the user has only typed "take" but no item name:
        if not text:
            return getAllFirstDescWords(worldRooms[location][GROUND])

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for item in list(set(worldRooms[location][GROUND])):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text) and worldItems[item].get(TAKEABLE, True):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique


    def complete_drop(self, text, line, begidx, endidx):
        possibleItems = []
        itemToDrop = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)

        for descWord in invDescWords:
            if line.startswith('drop %s' % (descWord)):
                return [] # command is complete

        # if the user has only typed "drop" but no item name:
        if itemToDrop == '':
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(text):
                possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

    def do_look(self, arg):
        """Look at an item, direction, or the area:
"look" - display the current area's description
"look <direction>" - display the description of the area in that direction
"look exits" - display the description of all adjacent areas
"look <item>" - display the description of an item on the ground in storage or in your inventory"""

        lookingAt = arg.lower()
        if lookingAt == '':
            # "look" will re-print the area description
            displayLocation(location, default)
            return

        if lookingAt == 'exits':
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in worldRooms[location]:
                    print('%s: %s' % (direction.title(), worldRooms[location][direction]))
            return

        if lookingAt in ('north', 'west', 'east', 'south', 'up', 'down', 'n', 'w', 'e', 's', 'u', 'd'):
            if lookingAt.startswith('n') and NORTH in worldRooms[location]:
                print(worldRooms[location][NORTH])
            elif lookingAt.startswith('w') and WEST in worldRooms[location]:
                print(worldRooms[location][WEST])
            elif lookingAt.startswith('e') and EAST in worldRooms[location]:
                print(worldRooms[location][EAST])
            elif lookingAt.startswith('s') and SOUTH in worldRooms[location]:
                print(worldRooms[location][SOUTH])
            elif lookingAt.startswith('u') and UP in worldRooms[location]:
                print(worldRooms[location][UP])
            elif lookingAt.startswith('d') and DOWN in worldRooms[location]:
                print(worldRooms[location][DOWN])
            else:
                print('There is nothing in that direction.')
            return

        # see if the item being looked at is on the ground at this location or in storage.
        #item = getFirstItemMatchingDesc(lookingAt, worldRooms[location][GROUND][STORAGE])
        item = getFirstItemMatchingDesc(lookingAt, worldRooms[location][GROUND])
        if item != None:
            print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))
            return

        # see if the item being looked at is in the inventory
        item = getFirstItemMatchingDesc(lookingAt, inventory)
        if item != None:
            print('\n'.join(textwrap.wrap(worldItems[item][LONGDESC], SCREEN_WIDTH)))
            return
            
        
        print('You do not see that nearby.')
    
            

    def complete_look(self, text, line, begidx, endidx):
        possibleItems = []
        lookingAt = text.lower()

        # get a list of all "description words" for each item in the inventory
        invDescWords = getAllDescWords(inventory)
        groundDescWords = getAllDescWords(worldRooms[location][GROUND])

        for descWord in invDescWords + groundDescWords + [NORTH, SOUTH, EAST, WEST, UP, DOWN]:
            if line.startswith('look %s' % (descWord)):
                return [] # command is complete
                

        # if the user has only typed "look" but no item name, show all items on ground  and directions:
        if lookingAt == '':
            possibleItems.extend(getAllFirstDescWords(worldRooms[location][GROUND][STORAGE]))
            for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
                if direction in worldRooms[location]:
                    possibleItems.append(direction)
            return list(set(possibleItems)) # make list unique

        # otherwise, get a list of all "description words" for ground items matching the command text so far:
        for descWord in groundDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        # check for matching directions
        for direction in (NORTH, SOUTH, EAST, WEST, UP, DOWN):
            if direction.startswith(lookingAt):
                possibleItems.append(direction)

        # get a list of all "description words" for inventory items matching the command text so far:
        for descWord in invDescWords:
            if descWord.startswith(lookingAt):
                possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique

        #arg = arg.lower()
    
    # Extra ways of writing commands
    do_read = do_look
    do_l = do_look
    
    def do_eat(self, arg):
        """"eat <item>" - eat an item in your inventory."""
        itemToEat = arg.lower()

        if itemToEat == '':
            print('Eat what? Type "inventory" or "inv" to see whats in your inventory.')
            return

        cantEat = False

        for item in getAllItemsMatchingDesc(itemToEat, inventory):
            if worldItems[item].get(EDIBLE, False) == False:
                cantEat = True
                continue # there may be other items named this that you can eat, so we continue checking
            # NOTE - If you wanted to implement hunger levels, here is where
            # you would add code that changes the player's hunger level.
            print('You eat %s may your bowls forever question your terrible choices.' % (worldItems[item][SHORTDESC]))
            inventory.remove(item)
            return

        if cantEat:
            print('I dont think the "%s" would like you to do that...' % (worldItems[item][SHORTDESC]))
        else:
            print('You do not have "%s". Type "inventory" or "inv" to see what in your inventory.' % (itemToEat))


    def complete_eat(self, text, line, begidx, endidx):
        itemToEat = text.lower()
        possibleItems = []

        # if the user has only typed "eat" but no item name:
        if itemToEat == '':
            return getAllFirstDescWords(inventory)

        # otherwise, get a list of all "description words" for edible inventory items matching the command text so far:
        for item in list(set(inventory)):
            for descWord in worldItems[item][DESCWORDS]:
                if descWord.startswith(text) and worldItems[item].get(EDIBLE, False):
                    possibleItems.append(descWord)

        return list(set(possibleItems)) # make list unique
        
        
    do_exit = do_quit # another way of exiting the game with a differnt word
    
    def do_clear(self, arg):
        """"clear" - Clear all text from the screen."""
        if platform.system == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    # :)
    def do_hacf(self, arg):
        if 'Troll' in worldRooms['Main Hall'][STORAGE]:
            print(bcolors.start + 'A patch will be released soon, you have compinsated, please do not take us to court.' + bcolors.end)
        
        else:
            """hacf - ### ?????? ###"""
            fake_error = ValueError('ERROR : The spacetime continum has been breached, all you know is a lie.')
            print(fake_error)
            print(bcolors.start + "The developer is sorry for this bug, we have deposited something nice for you in the chest." + bcolors.end)
            #worldItems[item][DESCWORDS]
            item = 'Troll'
            worldRooms['Main Hall'][STORAGE].append(item)
            worldRooms['Main Hall'][GROUND].remove(item)
        
        

                
        
if __name__ == '__main__':
    print(bcolors.start + '  Escape the house  ' + bcolors.end)
    print('====================')
    print("")
    print('[Type "help" for commands.]')
    print("")
    displayLocation(location, default)
    TextAdventureCmd().cmdloop()
    
    if len(STORAGE) > 15:
        print("You hear a soft click, could it be a trap?, Gnomes?!, *GASP* swamp folk... the worst, no its just the door opening, you are free to leave.")
        print("Congratulations are in order, you found evenything however turns out you could have just opened the door it was never locked at all... good job though..")
    print('Looks like you are going to be stuck here for a very, very long time.')
