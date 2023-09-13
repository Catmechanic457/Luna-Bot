from random import choice
from data_root import Data

class Custom_Interactions(Data) :
    def __init__(self, data_directory : str, type : str, id : int) -> None :
        self.type = type
        self.id = str(id)
        super().__init__(data_directory)

        # Add the item if it doesn't exist
        if not self.item_exists(self.type, self.id) :
            self.add_item(self.type, self.id)
        
        if not "interactions" in self.data()[self.type][self.id] :
            data = self.data()
            data[self.type][self.id]["interactions"] = {
                "exclusive": {},
                "contains": {}
            }
            self.write(data)
    
    # Define len() attribute
    def __len__(self) -> int :
        groups = ["exclusive", "contains"]
        length = 0
        for group in groups :
            length += len(self.get()[group])
        return length
    
    def get(self) -> dict[str, dict[str,str]] :
        return self.data()[self.type][self.id]["interactions"]
    
    def add(self, trigger : str, responses : list[str], group : str = "exclusive") -> None :

        data = self.data()
        if trigger in self.get()[group] : data[self.type][self.id]["interactions"][group][trigger].extend(responses)
        else : data[self.type][self.id]["interactions"][group][trigger] = responses
        self.write(data)
    
    def delete(self, trigger : str, group : str = "exclusive") -> None :
        data = self.data()
        data[self.type][self.id]["interactions"][group].pop(trigger)
        self.write(data)
    
    def interaction_exists(self, trigger, group) -> bool :
        return trigger in self.get()[group]
    
    def responses(self, message : str) -> list[str] :
        # Combine all responses into array
        responses = []
        interactions = self.get()
        responses.extend(interactions["exclusive"].setdefault(message, []))
        for trigger in interactions["contains"] :
            if trigger in message : responses.extend(interactions["contains"][trigger])
        
        return responses

class Custom_Interactions_Group :
    def __init__(self, directory : str, server_id : int, user_id : int) -> None:
        self.server_interactions = Custom_Interactions(directory, "server", server_id)
        self.user_interactions = Custom_Interactions(directory, "user", user_id)
    
    def __len__(self) -> int :
        return len(self.server_interactions) + len(self.user_interactions)
    
    def get_response(self, message : str) -> str | None :
        responses : list = self.server_interactions.responses(message)
        responses.extend(self.user_interactions.responses(message))
        if not responses : return None
        else : return choice(responses)
        
