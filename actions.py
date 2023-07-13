from random import *

class Action :
    def __init__(self, action_descriptions : list[str], positive_responses : list[str], negative_responses : list[str], rate_positive : int, rate_negative : int) -> int :
        self.action_descriptions = action_descriptions
        self.positive_responses = positive_responses
        self.negative_responses = negative_responses
        self.rate_positive = rate_positive
        self.rate_negative = -abs(rate_negative)
    
    def get_description(self) -> str :
        return choice(self.action_descriptions)
    
    def get_positive(self) -> str :
        return choice(self.positive_responses)
    def get_positive_score(self) -> int :
        return randint(self.rate_positive//2, self.rate_positive)
    
    def get_negative(self) -> str :
        return choice(self.negative_responses)
    def get_negative_score(self) -> int :
        return randint(self.rate_negative, self.rate_negative//2)

pet = Action(
    ["You pet Luna", "You stroke Luna"],
    ["She likes it", "She purrs", "She makes happy cat noises", "She is happy to be pet"],
    ["She suddenly scratches your arm", "She runs away immediately", "She'd rather be getting treats", "She doesn't like it"],
    150,-100
    )

tease = Action(
    ["You tease Luna with some treats", "You hold some treats just above Luna's head"],
    ["She purrs", "She makes happy cat noises", "She likes trying to snatch the treats"],
    ["She suddenly scratches your arm", "She doesn't like getting teased", "She gets frustrated"],
    200,-250
    )

balloon = Action(
    ["You give Luna a balloon to play with", "You give Luna balloon"],
    ["She bats it around, purring", "She happily plays with it", "She wacks it endlessly"],
    ["It suddenly pops", "She doesn't like it", "It pops immediately"],
    200,-200
    )

give_food = Action(
    ["You give Luna a big bowl of food", "You give Luna her daily portion of food", "You give Luna a big scoop of cat food", "You feed Luna", "You give Luna a pile of food"],
    ["She gobbles it all immediately", "She devours it", "She inhales it like Kirby", "She munches on it", "She happily eats it"],
    ["She doesn't like the brand of pet-food", "She walks away without touching it", "She's suddenly not hungry", "She doesn't like it"],
    400,-100
)