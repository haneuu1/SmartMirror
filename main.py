from tListener import Listener
from CommandHandler import CommandHandler
import threading

listener = Listener()

command_handler = CommandHandler()
#mqtt sub
def command_listener():
    prev_command = None
    print('===command listener start')
    while True:
        curr_command = listener.run()  # Get the full phrase from the listener

        if (curr_command != prev_command and curr_command != ''):
            command_handler.add_command(curr_command)
        
        prev_command = curr_command

if __name__=='__main__':
    command_handler.start()
    command_listener()