from random import *

class Responses :
    def caught_attention(self) -> str :
            response_pool = [
                "Huh? What?",
                "You Called?",
                "You Needed Me?",
                "What? Where?",
                "What is it?",
                "I SWEAR I JUST HEARD MY NAME",
                "WHO SAID THAT?"
            ]
            return choice(response_pool)
        
    def demon_spotted(self) -> str :
        response_pool = [
            "Stay back, Demon!",
            "That's the laugh of the devil...",
            "Ahhh! Demon!",
            "Get away ya Demon!",
            "nonono You Get back, Demon!",
            "Why does that laugh sound so demonic?",
            "\*hisses\*"
        ]
        return choice(response_pool)
    
    def shiny_spotted(self) -> str :
        response_pool = [
            "Omgo it's sparkly!",
            "^_^ Sparkly",
            "Ohh it shiny",
            ":sparkles:",
            ":sparkles: :sparkles:",
            ":sparkles: :sparkles: :sparkles:"
        ]
        if randint(0,1) == 0 :
            return "{} {}".format(choice(response_pool), self.emoticon_reaction())
        
        return choice(response_pool)
    
    def reaction(self) -> str :
        response_pool = [
            "OMGO",
            "omgo",
            "lovely",
            "woozy",
            ":sparkles: wozzy :sparkles:",
            ":sparkles: lovely :sparkles:",
            ":sparkles:",
            ":sparkles: :sparkles:",
            ":sparkles: :sparkles: :sparkles:"
        ]
        if randint(0,1) == 0 :
            return "{} {}".format(choice(response_pool), self.emoticon_reaction())
        
        return choice(response_pool)
    
    def emoticon_reaction(self) -> str :
        response_pool = [
            "ฅ⁠^⁠•⁠ﻌ⁠•⁠^⁠ฅ",
            "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "^_^",
            "=^..^=",
            "~(^._.)",
            "(っ◕‿◕)っ",
            "=^..^= ~(^._.) (っ◕‿◕)っ"
        ]
        return choice(response_pool)
        
    
    def grant_sleep(self) -> str :
        response_pool = [
            "Night",
            "Night Night",
            "Noight",
            "Noight Noight",
            "Ima go slep too",
            "Yes... Sleep, Child"
        ]
        if randint(0,1) == 0 :
            return "{} {}".format(choice(response_pool), self.emoticon_reaction())
        
        return choice(response_pool)
    
    def not_kitten(self) -> str :
        response_pool = [
            "I'm not a kitten I'm a cat",
            "Don't call me a child!",
            "I'm not that young...",
            "Oh please im a CAT",
            "I aint no CHILD",
            "I'M NOT A KITTEN",
            "I'M NOT A CHILDDD"
        ]
        return choice(response_pool)
    
    def meow(self) -> str :
        response_pool = [
            "Meow?",
            "Meow",
            "Mau",
            "Meeoowww",
            "Mewww",
            "Maouu",
            "MMeeow",
            "M E O W",
            "m e o w",
            "moo",
            "\*purrs\*",
            "\*happy cat noises\*"
        ]

        if randint(0,1) == 0 :
            return "{} {}".format(choice(response_pool), self.emoticon_reaction())
        
        return choice(response_pool)