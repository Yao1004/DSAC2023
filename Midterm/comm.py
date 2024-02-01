import socket
import time
from copy import deepcopy
import sys

IP = '127.0.0.1'
PORT = 48763
BEAT = 130*16
SPEED = 120

ms_per_beat = int((60/SPEED)/16 * 1000 * 4)
s_per_beat = (60/SPEED)/16 * 4
music  = [[] for i in range(BEAT)]

class Send:

    def __init__(self) : # section and beat are 1-based
        self.instrument = 0
        self.midi = 0
        self.volume = 0
        self.duration = 0

def readnote (string, section, instrument) :
    
    global music
    midi_str, beat, volume, duration = string.split()
    beat = int(beat)
    volume = int(volume)
    duration = int(duration)
    tmp = Send()
    dct = {'C':60, 'D':61, 'E':63, 'F':65, 'G':67, 'A':68, 'B':70}
    tmp.midi = dct[midi_str[0]] + (int(midi_str[1])-4)*12
    tmp.volume = volume
    tmp.duration = duration * ms_per_beat
    tmp.instrument = instrument
    music[(section-1+3)*16+(beat-1)].append(deepcopy(tmp))

def readsound (string, section, instrument) :
    
    global music
    type, beat, volume = string.split()
    beat = int(beat)
    volume = int(volume)
    tmp = Send()
    dct = {'D':0, 'C':1, 'R':2, 'Z':3, 'B':4}
    tmp.midi = dct[type[0]] + int(type[1])
    tmp.volume = volume
    tmp.duration = 0
    tmp.instrument = instrument
    music[(section-1+3)*16+(beat-1)].append(deepcopy(tmp))
begin = 0
if len(sys.argv) == 1 :
    begin = 0
elif len(sys.argv) == 2 :
    begin = int(sys.argv[1])*16
else :
    exit(1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
scores = ['./textfile/piano.txt', './textfile/string.txt', './textfile/cello.txt']
sounds = ['./textfile/drum.txt', './textfile/sound.txt']

for fp in range(len(scores)):
    with open(scores[fp], 'r') as f :
        while True :
            line = f.readline()
            if line is None or line == '':
                break
            sct, num = line.split()
            for i in range(int(num)) :
                readnote(f.readline(), int(sct), fp)

for fp in range(len(sounds)):
    with open(sounds[fp], 'r') as f :
        while True :
            line = f.readline()
            if line is None or line == '':
                break
            sct, num = line.split()
            for i in range(int(num)) :
                readsound(f.readline(), int(sct), fp + len(scores))


for i in range(begin, len(music)) :
    for m in music[i]: 
        d = (m.instrument << 32) + (m.midi << 24) + (m.volume << 16) + (m.duration << 0)
        sock.sendto(d.to_bytes(5, byteorder='big'), (IP, PORT))
    time.sleep(s_per_beat)

sock.shutdown(socket.SHUT_RDWR)
sock.close()