
from luna import *
from data_root import Data

class User_Settings(Data) :
    def __init__(self, data_directory : str, id : int) -> None :
        self.id = str(id)
        super().__init__(data_directory)

        # Add the item if it doesn't exist
        if not self.item_exists("user", self.id) :
            self.add_item("user", self.id)
        
        if not "settings" in self.data()["user"][self.id] :
            data = self.data()
            data["user"][self.id]["settings"] = {
                "blocked_users" : [],
                "accept_whisper" : True
            }
            self.write(data),
    
    def get(self) -> int :
        return self.data()["user"][self.id]["settings"]
    
    def get_setting(self, setting : str) :
        return self.get()[setting]

    def edit_setting(self, setting : str, value) -> None :
        data = self.data()
        data["user"][self.id]["settings"][setting] = value
        self.write(data)
    
    def block(self, user_id : int) -> None :
        data = self.data()
        data["user"][self.id]["settings"]["blocked_users"].append(user_id)
        self.write(data)
    
    def unblock(self, user_id : int) -> None :
        data = self.data()
        data["user"][self.id]["settings"]["blocked_users"].remove(user_id)
        self.write(data)