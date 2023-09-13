from data import Data_File

class Substitutions(Data_File) :
    def substitute(self, string : str) -> str :
        return self.data().setdefault(string, string)