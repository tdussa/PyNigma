# PyNigma - Python Enigma Emulator

This Python script is a simple Enigma emulator, inspired by
  https://summersidemakerspace.ca/projects/enigma-machine/
and
  https://cryptii.com/pipes/enigma-machine

It has been created out of the desire to have something that runs on the
command line to facilitate a certain measure of brute-forcing.

It currently implements three rotors only.

Supported rotors:
+ I
+ II
+ III
+ IV
+ V
+ VI
+ VII
+ VIII

Supported reflectors:
+ A
+ B
+ C

Supported features are rotor selection, rotor ring setup, reflector
selection, initial rotor setup, and plugboard settings.

The script tries to be smart and do the right thing when settings are
specified.  For instance,
+ `-r I,II,III`
+ `-r "I II III"`
+ `-r "I, II, III"`
+ `-r I/II/III`

all select rotors I, II, and III.

Examples for identical rotor ring settings:
+ `-R 1,2,3`
+ `-R 1/2/3`
+ `-R A,B,C`
+ `-R ABC`

Examples for identical inital rotor setups:
+ `-s ABC`
+ `-s A,B,C`
+ `-s "A B C"`
+ `-s A/B/C`

Examples for identical plugboard setups:
+ `-p "AB CD EF GH IJ KL"`
+ `-p AB,CD,EF,GH,IJ,KL`
+ `-p AB/CD/EF/GH/IK,KL`

The script also supports verbose output that also gives information about
the parameters used and the final internal state.  Finally, it can provide
stepwise information about the internal state, intended for debugging
and/or to help understanding the workings of the enigma.
