from data import Data_File

class Config(Data_File) :
    def root(self) -> str :
        return {
            "token" : None,
            "whitelist" : []
        }
    
    def get_token(self) -> str :
        return self.data()["token"]
    
    def whitelist(self) -> list[str] :
        return self.data()["whitelist"]