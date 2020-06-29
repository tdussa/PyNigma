#! /usr/bin/env python
# -*- coding: utf-8 -*-

# PyNigma - a Python Enigma Emulator
# Copyright (C) 2020 Tobias Dussa <tobias-pynigma@dussa.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from argparse import ArgumentParser
import sys


#
# Component definitions, taken from
# https://en.wikipedia.org/wiki/Enigma_rotor_details
# https://en.wikipedia.org/wiki/Enigma_machine
# https://de.wikipedia.org/wiki/Enigma_(Maschine)
#
# Rotors (Walzen)
rotorsRaw = {
    'I':    'EKMFLGDQVZNTOWYHXUSPAIBRCJ',
    'II':   'AJDKSIRUXBLHWTMCQGZNPYFVOE',
    'III':  'BDFHJLCPRTXVZNYEIWGAKMUSQO',
    'IV':   'ESOVPZJAYQUIRHXLNFTGKDCMWB',
    'V':    'VZBRGITYUPSDNHLXAWMJQOFECK',
    'VI':   'JPGVOUMFYQBENHZRDKASXLICTW',
    'VII':  'NZJHGRCXMYSWBOUFAIVLPEKQDT',
    'VIII': 'FKQHTLXOCBJSPDZRAMEWNIUYGV',
}
rotors = {}
rotorsInv = {}
for rotor in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']:
    rotors[rotor] = {}
    rotorsInv[rotor] = {}
    for item in range(26):
        rotors[rotor][item] = ord(rotorsRaw[rotor][item])-ord('A')
        rotorsInv[rotor][ord(rotorsRaw[rotor][item])-ord('A')] = item

# Rotor turnovers (Walzenweiterschaltung)
rotorTurnoversRaw = {
    'I':    ['R'],
    'II':   ['F'],
    'III':  ['W'],
    'IV':   ['K'],
    'V':    ['A'],
    'VI':   ['A', 'N'],
    'VII':  ['A', 'N'],
    'VIII': ['A', 'N'],
}
rotorTurnovers = {}
for rotor in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']:
    rotorTurnovers[rotor] = [ord(x)-ord('A') for x in rotorTurnoversRaw[rotor]]


# Reflectors (Umkehrwalzen)
reflectorsRaw = {
    'A': 'EJMZALYXVBWFCRQUONTSPIKHGD',
    'B': 'YRUHQSLDPXNGOKMIEBFZCWVJAT',
    'C': 'FVPJIAOYEDRZXWGCTKUQSBNMHL',
}
reflectors = {}
for reflector in ['A', 'B', 'C']:
    reflectors[reflector] = {}
    for item in range(26):
        reflectors[reflector][item] = ord(reflectorsRaw[reflector][item])-ord('A')



# Settings struct
settings = {
    'rotors':    [ 'I', 'II', 'III' ],
    'rings':     [ 1, 1, 1 ],
    'setup':     [ 'A', 'A', 'A' ],
    'reflector': 'B',
}
settings['plugboard'] = {}
for item in range(26):
    settings['plugboard'][item] = item


#
# Helper functions
#

# Split parameter string into list, normalizing it
# For splitting, this function in particular accepts a number of delimiter
# characters (or strings)
def split_parameter(input):
    for delimiter in [',', '.', ';', ':', '-', '_', '+', '/']:
        input = input.replace(delimiter, ' ')
    return(input.upper().split())


# Argument parsing
parser = ArgumentParser()
parser.add_argument('-F', '--reflector', dest='reflector', help='specify reflector to be used (default: {default})'.format(default='B'))
parser.add_argument('-p', '--plugboard', dest='plugboard', help='specify plugboard to be used (default: none)')
parser.add_argument('-r', '--rotors',    dest='rotors',    help='specify rotors to be used (default: {default})'.format(default='I, II, III'))
parser.add_argument('-R', '--rings',     dest='rings',     help='specify rotor ring setup (default: {default})'.format(default='1, 1, 1'))
parser.add_argument('-s', '--setup',     dest='setup',     help='specify initial rotor setup (default: {default})'.format(default='A, A, A'))
parser.add_argument('-S', '--stepwise',  dest='stepwise',  default=False, action='store_true', help='print output stepwise')
parser.add_argument('-v', '--verbose',   dest='verbose',   default=False, action='store_true', help='increase verbosity')
parser.add_argument('inputfiles', nargs='*', default='-',  help='message to be encrypted; STDIN will be used if no message and no input file specified')
args = parser.parse_args()

# Process reflector settings
if args.reflector:
    settings['reflector'] = args.reflector.upper()
    if not settings['reflector'] in reflectorsRaw:
        print('ERROR: Illegal reflector specification: {}.  Only reflectors A, B, and C supported.'.format(settings['reflector']))
        sys.exit(1)

# Process plugboard settings
plugboard = []
if args.plugboard:
    plugboard = split_parameter(args.plugboard)
    if not (len(plugboard)) in range(14):
        print('ERROR: Illegal plugboard specification: {}.  Maximum number of plugs is 13.'.format(plugboard))
        sys.exit(1)
    if not (min(len(x) for x in plugboard) == 2) or \
       not (max(len(x) for x in plugboard) == 2):
        print('ERROR: Illegal plugboard specification: {}.  Every plug must have exactly 2 letters.'.format(plugboard))
        sys.exit(2)
    if not len(set(''.join(plugboard))) == 2*len(plugboard):
        print('ERROR: Illegal plugboard specification: {}.  Every letter must only occur once.'.format(plugboard))
        sys.exit(3)
    if not ''.join(plugboard).isalpha():
        print('ERROR: Illegal plugboard specification: {}.  Plug specifications can only contain letters.'.format(plugboard))
        sys.exit(4)
    for plug in plugboard:
        settings['plugboard'][ord(plug[0])-ord('A')] = ord(plug[1])-ord('A')
        settings['plugboard'][ord(plug[1])-ord('A')] = ord(plug[0])-ord('A')

# Process rotor settings
if args.rotors:
    settings['rotors'] = split_parameter(args.rotors)
    if not len(settings['rotors']) == 3:
        print('ERROR: Illegal number of rotors: {}.  Only three rotors supported.'.format(len(settings['rotors'])))
        sys.exit(5)
    for rotor in settings['rotors']:
        if not rotor in rotorsRaw:
            print('ERROR: Illegal rotor specification: {}.  Only rotors I, II, III, IV, V, VI, VI, VII, and VIII supported.'.format(rotor))
            sys.exit(6)

# Process rotor ring settings
if args.rings:
    settings['rings'] = split_parameter(args.rings)
    if len(settings['rings']) == 1:
        settings['rings'] = list(settings['rings'][0])
    if not len(settings['rings']) == 3:
        print('ERROR: Illegal number of rotor ring settings: {}.  Must be equal to the number of rotors.'.format(args.rings))
    rings = []
    for ring in settings['rings']:
        if ring.isalpha():
            if not len(ring) == 1:
                print('ERROR: Illegal rotor ring setting: {}.  Must be an integer between 1 and 26 or a single letter.'.format(ring))
                sys.exit(1)
            rings.append(ord(ring)-ord('A')+1)
        else:
            if ring.isdigit():
                if not (int(ring)-1) in range(26):
                    print('ERROR: Illegal rotor ring setting: {}.  Must be an integer between 1 and 26 or a single letter.'.format(ring))
                    sys.exit(1)
                rings.append(int(ring))
            else:
                print('ERROR: Illegal rotor ring setting: {}.  Must be an integer between 1 and 26 or a single letter.'.format(ring))
                sys.exit(1)
    settings['rings'] = rings

# Process rotor ring setup
if args.setup:
    settings['setup'] = split_parameter(args.setup)
    if len(settings['setup']) == 1:
        settings['setup'] = list(settings['setup'][0])
    if not len(settings['setup']) == 3:
        print('ERROR: Illegal number of setups: {}.  Must be equal to the number of rotors.'.format(args.setup))
    setups = []
    for setup in settings['setup']:
        if setup.isalpha():
            if not len(setup) == 1:
                print('ERROR: Illegal rotor setup: {}.  Must be an integer between 1 and 26 or a single letter.'.format(setup))
                sys.exit(1)
            setups.append(setup)
        else:
            if setup.isdigit():
                if not (int(setup)-1) in range(26):
                    print('ERROR: Illegal rotor setup: {}.  Must be an integer between 1 and 26 or a single letter.'.format(setup))
                    sys.exit(1)
                setups.append(chr(int(setup)-1+ord('A')))
            else:
                print('ERROR: Illegal rotor setup: {}.  Must be an integer between 1 and 26 or a single letter.'.format(setup))
                sys.exit(1)
    settings['setup'] = setups


if args.verbose:
    print('Rotors used: {}.'.format(', '.join(settings['rotors'])))
    print('Rotor ring setup: {} ({}).'.format(''.join([(chr(x+ord('A')-1)) for x in settings['rings']]), ', '.join([str(x) for x in settings['rings']])))
    print('Reflector used: {}.'.format(settings['reflector']))
    print('Plugboard used: {}.'.format(', '.join(plugboard)))
    print('Initial setup: {} ({}).'.format(''.join(settings['setup']), ', '.join([str(ord(x)-ord('A')+1) for x in settings['setup']])))
    if args.stepwise:
        print('Stepwise display enabled.')
        

#
# Encrypt a single letter
# Input: letter, current rotor state, settings (default used is left empty)
# Output: chiletter, new rotor state
#
def encryptLetter(letter, status, settings=settings):
    # If not a letter, skip processing and return the input, leaving the
    # status untouched
    if not letter.isalpha():
        chiletter = letter
    else:
        # Normalize input to uppercase characters and shift it from ASCII
        # space into number space
        letter = letter.upper()
        letter = ord(letter) - ord('A')
        
        # Shift the rotors
        # Slow rotor steps if middle rotor hits a turnover
        # This is independent of the motion of the fast rotor; furthermore,
        # if the slow rotor steps, then then middle rotor steps again as
        # well due to the way the mechanics work (this is the "Enigma
        # anomaly")
        if ((status[1]+1) % 26) in rotorTurnovers[settings['rotors'][1]]:
            status[0] += 1
            status[0] %= 26
            status[1] += 1
            status[1] %= 26
        # Middle rotor steps if fast rotor hits a turnover
        if ((status[2] + 1) % 26) in rotorTurnovers[settings['rotors'][2]]:
            status[1] += 1
            status[1] %= 26
        # Fast rotor steps every time
        status[2] += 1
        status[2] %= 26

        # Plugboard inbound
        chiletter = settings['plugboard'][letter]

        # Rotors inbound
        # The rotor wiring must be shifted by the current status of the
        # rotor, which is the amount by which it is rotated.  Thus, the
        # physical contacts of the rotor are shifted by the same amount.
        #   -> + status[rotor]
        # Furthermore, the status contains the indicator letter that would
        # be visible on the actual machine.  The initial ring setup changes
        # this, so the correction must be corrected for the ring setup.
        #   -> - settings['rings'][rotor]
        # Finally, the ring setup assigns numbers 1 through 26, so the
        # rotor labels are shifted by 0 through 25 positions, respectively.
        # This off-by-one error must also be corrected for.
        #   -> + 1
        # All in all, the correction is
        #   -> + status[rotor] - settings['rings'][rotor] + 1
        # After encoding, the entire correction process must be reversed
        # to get from the virtual output to the physical connector.
        #   -> - status[rotor] + settings['rings'][rotor] - 1
        # All modulo 26, of course.
        for rotor in reversed(range(len(settings['rotors']))):
            chiletter = (rotors[settings['rotors'][rotor]][(chiletter + status[rotor] - settings['rings'][rotor] + 1) % 26] - status[rotor] + settings['rings'][rotor] - 1) % 26

        # Reflector
        chiletter = reflectors[settings['reflector']][chiletter]

        # Rotors outbound
        # The rotor wiring must be shifted by the current status of the
        # rotor, which is the amount by which it is rotated.  Thus, the
        # physical contacts of the rotor are shifted by the same amount.
        #   -> + status[rotor]
        # Furthermore, the status contains the indicator letter that would
        # be visible on the actual machine.  The initial ring setup changes
        # this, so the correction must be corrected for the ring setup.
        #   -> - settings['rings'][rotor]
        # Finally, the ring setup assigns numbers 1 through 26, so the
        # rotor labels are shifted by 0 through 25 positions, respectively.
        # This off-by-one error must also be corrected for.
        #   -> + 1
        # All in all, the correction is
        #   -> + status[rotor] - settings['rings'][rotor] + 1
        # After encoding, the entire correction process must be reversed
        # to get from the virtual output to the physical connector.
        #   -> - status[rotor] + settings['rings'][rotor] - 1
        # All modulo 26, of course.
        for rotor in range(len(settings['rotors'])):
            chiletter = (rotorsInv[settings['rotors'][rotor]][(chiletter + status[rotor] - settings['rings'][rotor] + 1) % 26] - status[rotor] + settings['rings'][rotor] - 1) % 26

        # Plugboard outbound
        chiletter = settings['plugboard'][chiletter]

        # Shift it back from number space into ASCII space
        chiletter = chr(chiletter + ord('A'))

    # Return the encrypted letter and the new status
    return(chiletter, status)


#
# Encrypt a message
# Input: message, settings (default used if left empty)
# Output: chimessage
#
def encryptMessage(message, settings=settings):
    # Initialize the current status with the basic settings,
    # taking into account the ring settings and the start setup
    status = [(ord(x)-ord('A')) for x in settings['setup']]

    # Encrypt the message using the starting setup
    chitext = ''
    for letter in message:
        chiletter, status = encryptLetter(letter, status)
        chitext += chiletter
        if args.stepwise:
            print('Status: {status}, chitext: {chitext}'.format(chitext=chitext, status=''.join([chr(x+ord('A')) for x in status])))
    return(chitext, ''.join([chr(x+ord('A')) for x in status]))




#
# Process input files
# 
for inputfile in args.inputfiles:
    if inputfile == '-':
        if args.verbose:
            print('Processing message from STDIN.')
        message = ''
        for line in sys.stdin:
            message += line
    else:
        if args.verbose:
            print('Processing message file {}.'.format(inputfile))
        with open(inputfile, 'r') as messagefile:
            message = messagefile.read()

    if not message == '':
        chitext, status = encryptMessage(message)
        if args.verbose:
            print('Final status: {status}\nEncrypted message:\n{chitext}'.format(chitext=chitext, status=status))
        else:
            print(chitext)
