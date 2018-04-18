#!/home/anton/venv/bin/python
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

args = parser.parse_args()
# header ends here

# [[file:~/Code/Python/NewSounds/literate.org::queue-helpers][queue-helpers]]
def read_queue():
    with open('stack', 'rb') as f:
        try:
            deq = pickle.load(f)
        except:
            deq = deque()
    print('In read {}'.format(deq))
    return deq

def write_queue(q):
    with open('stack', 'wb') as f:
        pickle.dump(q, f)
        #f.write(pickle.dumps(q))

def listen(name):
   #Not used currently
   os.system("xsel | tr '\n' ' ' | espeak -p 100 -s 650 -v male7 -w {}.wav --stdin".format(name))
# queue-helpers ends here

# [[file:~/Code/Python/NewSounds/literate.org::enqueue][enqueue]]
def add_to_stack():
    '''Enqueues items on the right end of the queue, write out to the queue persistance file,
       create an text to speech file.
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
        os.system("xsel | tr '\n' ' ' | espeak -p 100 -s 650 -v male7 -w {}.wav --stdin".format(name))
    #Delete all files not on the queue.
# enqueue ends here

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
# dequeue ends here

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
# concat ends here

# [[file:~/Code/Python/NewSounds/literate.org::dispatcher][dispatcher]]
if __name__ == "__main__":
    if args.add:
        add_to_stack()
    if args.play:
        pop_from_stack()
    if args.join:
        concat_files()
# dispatcher ends here
