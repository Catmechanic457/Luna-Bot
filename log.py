from time import strftime

def timestamp() -> str :
    return strftime("[%d-%m-%Y, %H:%M:%S]")

class Logs :
    def __init__(self, log_file) -> None:
        self.directory = log_file
    
    def log(self, message : str, include_timestamp : bool = True, print_in_console : bool = True) -> None :
        log = f'{f"{timestamp()} " if include_timestamp else ""}{message}'
        if print_in_console : print(log)
        file = open(f'{self.directory}log-{strftime("%d-%m-%Y")}.txt', "a", encoding="utf-8")
        try :
            file.write(f'{log}\n')
        except Exception as e:
            print(e)
        file.close()