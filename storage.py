
class Storage :
    def __init__(self, primary_directory = "data/", settings_file = "settings.txt", config_file = "config.txt") :
        self.directory_lookup = {
            "primary_directory" : primary_directory,
            "settings_file" : settings_file,
            "config_file" : config_file
        }
    
    def get(self, item_id : str) :
        return self.directory_lookup[item_id]
    
    def find_content(self, file_location, header : str) :
        file = open(file_location, "r")
        all_content = file.readlines()
        file.close()
        found_header = False
        for item in all_content :
            if not found_header :
                if item.replace("\n", "") == "<{}>".format(header) :
                    found_header = True
            else : return item.replace("\n", "")