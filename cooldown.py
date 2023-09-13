from data import Data_File
import time

def in_seconds(seconds : int = 0, minutes : int = 0, hours : int = 0, days : int = 0) -> int :
    return seconds + (minutes * 60) + (hours * 3600) + (days * 86400)

class Cooldown(Data_File) :
    def __init__(self, directory: str, user_id : int, task_id : str) -> None :
        super().__init__(directory)
        self.id = str(user_id)
        self.task_id = task_id

        if not self.id in self.data() :
            data = self.data()
            data[self.id] = {}
            self.write(data)
        
        if not self.task_id in self.data()[self.id] :
            data = self.data()
            data[self.id][self.task_id] = 0
            self.write(data)

    def mark(self, cooldown_seconds : int) -> None :
        epoch = int(time.time())
        data = self.data()
        data[self.id][self.task_id] = epoch + cooldown_seconds
        self.write(data)
    
    def mark_given(self, target_epoch : int) -> None :
        data = self.data()
        data[self.id][self.task_id] = target_epoch
        self.write(data)
    
    def able(self) -> bool :
        return self.delta() <= 0
    
    def delta(self) -> int :
        return int(self.data()[self.id][self.task_id]) - int(time.time())
    
    def formatted_delta(self) -> str :
        days = self.delta()//in_seconds(days=1)
        if days : return f'{days} day{"s" if days > 1 else ""}'
        hours = self.delta()//in_seconds(hours=1)
        if hours : return f'{hours} hour{"s" if hours > 1 else ""}'
        minutes = self.delta()//in_seconds(minutes=1)
        if minutes : return f'{minutes} minute{"s" if minutes > 1 else ""}'
        seconds = self.delta()//in_seconds(seconds=1)
        return f'{seconds} second{"s" if seconds > 1 else ""}'