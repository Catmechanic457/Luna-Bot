import json
import os

class Data_File :
    def __init__(self, directory : str) -> None:
        self.directory = directory

        if not os.path.isfile(self.directory) :
            self.write(self.root())
    
    def __len__(self) -> int :
        return len(self.data())
    
    def data(self) -> dict :
        file = open(self.directory, encoding="utf-8")
        data = json.load(file)
        file.close()
        return data
    
    def write(self, data : dict) -> None :
        file = open(self.directory, "w", encoding="utf-8")
        json.dump(data, file, indent=4)
        file.close()

    def root(self) -> dict :
        return {}
    
    def get(self) -> dict :
        return self.data()