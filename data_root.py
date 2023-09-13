from data import Data_File

class Data(Data_File) :
    def root(self) -> dict :
        return {
            "server" : {},
            "user" : {}
        }
    
    def item_exists(self, type : str, id : int) -> bool :
        if id in self.data()[type] : return True
        return False

    def add_item(self, type : str, id : int) -> None :
        data = self.data()
        data[type][id] = {}
        self.write(data)

class Manage(Data) :
    def users(self) -> dict :
        return self.data()["user"]
    def servers(self) -> dict :
        return self.data()["server"]
    def user_exists(self, id : int) -> bool :
        return str(id) in self.users()
    def server_exists(self, id : int) -> bool :
        return str(id) in self.servers()