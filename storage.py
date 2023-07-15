
class Storage :
    def __init__(self,
    primary_directory = "data/",
    settings_file = "settings.txt",
    config_file = "config.txt",
    user_data_directory = "user_data/",
    custom_interactions_directory = "custom_interactions/",
    custom_interactions_user = "user/",
    custom_interactions_server = "server/") :
        
        self.directory_lookup = {
            "primary_directory" : primary_directory,
            "settings_file" : settings_file,
            "config_file" : config_file,
            "user_data_directory" : user_data_directory,
            "custom_interactions_directory" : custom_interactions_directory,
            "custom_interactions_user" : custom_interactions_user,
            "custom_interactions_server" : custom_interactions_server
        }
    
    def get(self, item_id : str) -> str :
        return self.directory_lookup[item_id]
    
class Storage_File :

    def __init__(self, file_location : str) -> None :
        self.file_location = file_location

        
    def header_exists(self, header : str) -> bool :
        file = open(self.file_location, "r", encoding="utf-8")
        raw = file.readlines()
        file.close()

        for item in raw :
            if item.replace("\n", "") == "<{}>".format(header) :
                return True
        
        return False
    
    def find_content(self, header : str) -> str | None :
        file = open(self.file_location, "r", encoding="utf-8")
        raw = file.readlines()
        file.close()
        found_header = False
        for item in raw :
            if not found_header :
                if item.replace("\n", "") == "<{}>".format(header) :
                    found_header = True
            else : return item.replace("\n", "")
        return None
    
    def add_item(self, header : str, content : str) -> None :
        file = open(self.file_location, "a", encoding="utf-8")
        file.writelines("<{}>\n{}\n".format(header, content))
        file.close()
    
    def edit_content(self, header : str, content : str) -> None :
        if not self.header_exists(header) :
            return
        file = open(self.file_location, "r", encoding="utf-8")
        raw = file.readlines()
        file.close()

        file = open(self.file_location, "w", encoding="utf-8")
        found = False
        for line in raw :
            if not found :
                file.writelines(line)
                if line.replace("\n", "") == "<{}>".format(header) :
                    found = True

            else :
                found = False
                file.writelines("{}\n".format(content))
                

        file.close()
    
    def delete_item(self, header : str) -> None :
        file = open(self.file_location, "r", encoding="utf-8")
        raw = file.readlines()
        file.close()

        file = open(self.file_location, "w", encoding="utf-8")
        found = False
        for line in raw :
            if line.replace("\n", "") == "<{}>".format(header) :
                # Don't re-write header
                found = True

            elif found :
                # Don't re-write content
                found = False

            else : file.writelines(line) # Re-write everything else

        file.close()