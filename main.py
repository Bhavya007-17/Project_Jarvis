
from senses import Ear, Speaker
from brain import Brain
import time

def main():
    
    ear = Ear()
    mouth = Speaker()
    brain = Brain()
    
    mouth.speak("Systems online. Ready.")

    while True:
        
        if ear.listen_for_wake_word():
            mouth.speak("Yes?") 
            
            
            command = ear.listen_for_command()
            
            if command:
                
                response = brain.process_input(command)
                
                
                mouth.speak(response)
            else:
                mouth.speak("I didn't catch that.")
            
            
            time.sleep(0.5)

if __name__ == "__main__":
    main()