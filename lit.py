#!/usr/bin/python3
# [[file:~/Code/Python/NewSounds/literate.org::*Code][Code:1]]
# [[file:~/Code/Python/NewSounds/literate.org::header][header]]
import os
from hashlib import shake_256
import argparse
from collections import deque
import pickle
from pathlib import Path

home = str(Path.home())
os.chdir("{}/sound_files".format(home))

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--add", help="add a file",
                    action="store_true")
parser.add_argument("-p", "--play", help="play a file",
                    action="store_true")
parser.add_argument("-j", "--join", help="join all files",
                    action="store_true")
parser.add_argument("-l", "--list_files", help="list all files on queue",
                    action="store_true")
parser.add_argument("-s", "--speed", nargs='?', default='750',help="speed of recitation")
parser.add_argument("-i", "--pitch", nargs= '?', default='100', help="pitch of recitation")

args = parser.parse_args()

# header ends here #import statements and cli interface
# [[file:~/Code/Python/NewSounds/literate.org::queue-helpers][queue-helpers]]
def read_queue():
    '''Read the queue stored in stack, or create new one if an error occurs.
    Return the read in queue.'''
    with open('stack', 'rb') as f:
        try:
            deq = pickle.load(f)
        except:
            deq = deque()
            #Add a delete all wav files here.
    return deq

def write_queue(q):
    '''Write the queue q into 'stack'.'''
    with open('stack', 'wb') as f:
        pickle.dump(q, f)

# queue-helpers ends here #persist the queue on disk and read it
# [[file:~/Code/Python/NewSounds/literate.org::enqueue][enqueue]]
def add_to_stack():
    '''Enqueues items, write out to the queue persistance file,
       create a text to speech file with sha as name.
    '''
    m = shake_256()
    name = (os.popen("xsel").read())
    m.update(str.encode(name))
    name = m.hexdigest(16)
    t2t_queue = read_queue()
    on_filesystem = os.path.isfile("{}.wav".format(name))
    on_queue = (name in t2t_queue)
    if not on_queue:
        t2t_queue.append(name)
        write_queue(t2t_queue)
        print(t2t_queue)
    if not on_filesystem:
        os.system("xsel | tr '\n' ' ' | espeak -p {pitch} -s {speed} -v male7 -w {name}.wav --stdin"
        .format(name=name, speed=args.speed, pitch=args.pitch))
    #Delete all files not on the queue.

# enqueue ends here #Put the clipboard on the queue as an audio file
# [[file:~/Code/Python/NewSounds/literate.org::dequeue][dequeue]]
def pop_from_stack(delete=True):
    '''Dequeue a file from the left end of the queue.'''
    t2t_queue = read_queue()
    try:
        name = t2t_queue.popleft()
    except IndexError: 
        print('No files quequed up')
        os.system('rm *wav')
        return
    write_queue(t2t_queue)
    check = os.path.isfile("{}.wav".format(name))
    if not check: #see if you can use trys with os.system
        print('No file on disk')
    else:
        os.system('mplayer {}.wav'.format(name))
        if delete:
            os.system('rm {}.wav'.format(name))
        pop_from_stack()
# dequeue ends here #Remove an audio file and play it
# [[file:~/Code/Python/NewSounds/literate.org::concat][concat]]
def concat_files():
    '''Concat all the files in the queue'''
    #Badly tested.
    t2t_queue = read_queue()
    new_files = []
    for i in t2t_queue:
        check = os.path.isfile("{}.wav".format(i))
        if check:
            new_files.append(i)
    joined_command = ['{}.wav'.format(x) for x in new_files]
    joined_command = ' '.join(joined_command)
    os.system('sox {} big.wav'.format(joined_command))
    os.system('mplayer big.wav')
    os.system('rm *wav')
# concat ends here #Future options - not implemented
# [[file:~/Code/Python/NewSounds/literate.org::list][list]]
def list_files():
    k = read_queue()
    print("The size of the queue is {}".format(len(k)))
    for i in k:
        print(i)
# list ends here #List the files currently in the queue
# [[file:~/Code/Python/NewSounds/literate.org::dispatcher][dispatcher]]
if __name__ == "__main__":
    if args.add:
        add_to_stack()
    if args.play:
        pop_from_stack()
    if args.join:
        concat_files()
    if args.list_files:
        list_files()

# dispatcher ends here #cli interface mapping options to functions
# Code:1 ends here
