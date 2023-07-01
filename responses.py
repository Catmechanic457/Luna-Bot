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
        return choice(response_pool)
    
    def reaction(self) -> str :
        response_pool = [
            "OMGO",
            "omgo",
            "lovely",
            "woozy",
            ":sparkles: wozzy :sparkles:",
            ":sparkles: lovely :sparkles:",
            "^_^",
            ":sparkles:",
            ":sparkles: :sparkles:",
            ":sparkles: :sparkles: :sparkles:"
        ]
        return choice(response_pool)
    
    def emoticon_reaction(self) -> str :
        response_pool = [
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
        return choice(response_pool)