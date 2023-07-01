
class Storage :
    def __init__(self,
    primary_directory = "data/",
    settings_file = "settings.txt",
    config_file = "config.txt",
    custom_interactions_directory = "custom_interactions/",
    custom_interactions_user = "user/",
    custom_interactions_server = "server/") :
        
        self.directory_lookup = {
            "primary_directory" : primary_directory,
            "settings_file" : settings_file,
            "config_file" : config_file,
            "custom_interactions_directory" : custom_interactions_directory,
            "custom_interactions_user" : custom_interactions_user,
            "custom_interactions_server" : custom_interactions_server
        }
    
    def get(self, item_id : str) :
        return self.directory_lookup[item_id]
    
    def find_content(self, file_location, header : str) :
        file = open(file_location, "r", encoding="utf-8")
        all_content = file.readlines()
        file.close()
        found_header = False
        for item in all_content :
            if not found_header :
                if item.replace("\n", "") == "<{}>".format(header) :
                    found_header = True
            else : return item.replace("\n", "")