from storage import Storage_File
import os

class XP :
    def __init__(self, user_file_name : str) -> None :
        self.user_file_name = user_file_name
    
    def edit(self, amount : int) :
        user_file = Storage_File(self.user_file_name)
        if os.path.isfile(self.user_file_name) and user_file.header_exists("xp_points") :
            points = int(user_file.find_content("xp_points"))
            points += amount
            if points < 0 : points = 0
            user_file.edit_content("xp_points", str(points))
        else :
            if amount < 0 : amount = 0
            user_file.add_item("xp_points", str(amount))
    
    def total(self) :
        user_file = Storage_File(self.user_file_name)
        if os.path.isfile(self.user_file_name) and user_file.header_exists("xp_points") :
            points = int(user_file.find_content("xp_points"))
            return points
        else :
            return 0
    
    def formatted_total(self) -> tuple[int, int] :
        def req_experience(lvl : int) -> int :
            return int((((0.0001*lvl)**2) * 200000000) + 100)
            
        xp = self.total()
        lvl = 0

        while True :
            if xp - req_experience(lvl) >= 0 : 
                xp += - req_experience(lvl)
                lvl += 1
            else : return lvl, xp
    
    def level(self) -> int :
        return self.formatted_total()[0]

    def xp(self) -> int :
        return self.formatted_total()[1]
    
    def target(self) -> int :
        return int((((0.0001*self.level())**2) * 200000000) + 100)