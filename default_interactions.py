from luna import *

from random import *
from data import Data_File

class Responses(Data_File) :
    def caught_attention(self) -> str :
        return choice(self.data()["caught_attention"])
        
    def demon_spotted(self) -> str :
        return choice(self.data()["demon_spotted"])
    
    def shiny_spotted(self) -> str :
        if randint(0,1) == 0 :
            return f'{choice(self.data()["demon_spotted"])} {choice(self.data()["emoticon"])}'
        
        return choice(self.data()["shiny_spotted"])
    
    def reaction(self) -> str :
        if randint(0,1) == 0 :
            return f'{choice(self.data()["reaction"])} {choice(self.data()["emoticon"])}'
        
        return choice(self.data()["reaction"])
    
    def emoticon_reaction(self) -> str :
        return choice(self.data()["emoticon"])
        
    
    def grant_sleep(self) -> str :
        if randint(0,1) == 0 :
            return f'{choice(self.data()["grant_sleep"])} {choice(self.data()["emoticon"])}'
        
        return choice(self.data()["grant_sleep"])
    
    def not_kitten(self) -> str :
        return choice(self.data()["not_kitten"])
    
    def meow(self) -> str :
        if randint(0,1) == 0 :
            return f'{choice(self.data()["meow"])} {choice(self.data()["emoticon"])}'
        
        return choice(self.data()["meow"])

class Interaction :
    def __init__(self, response_function : str, description : str = "No Description") -> None :
        self.function = response_function
        self.description = description
    
    def __str__(self) -> str : return self.function()
    def get_description(self) -> str : return self.description

class Interactions(Responses) :

    def get_response(self, message) -> Interaction | None :
        return self.key().setdefault(message)
    
    def key(self) -> dict[str, Interaction] :

        caught_attention = Interaction(self.caught_attention, "Gets Luna's Attention")
        devil_spotted = Interaction(self.demon_spotted, "Luna senses demonic activity")
        reaction = Interaction(self.reaction, "Luna reacts with something cute")
        emoticon_reaction = Interaction(self.emoticon_reaction, "Luna reacts with a cute face")
        grant_sleep = Interaction(self.grant_sleep, "Luna wishes you a good night")
        shiny_spotted = Interaction(self.shiny_spotted, "Luna spots something shiny")
        not_kitten = Interaction(self.not_kitten, "Luna claims she is not that young")
        meow = Interaction(self.meow, "Luna meows")

        return {
            "ps": caught_attention,
            "luna": caught_attention,
            "food": emoticon_reaction,
            "treats": emoticon_reaction,
            "wozzy": reaction,
            "lovely": reaction,
            "omgo": reaction,
            "hehe": devil_spotted,
            "night": grant_sleep,
            "kitten": not_kitten,
            "meow": meow,
            ":sparkles:": shiny_spotted
        }