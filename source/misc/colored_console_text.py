class TextColor:
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'

class ColoredText:
    def __init__(self, text: str, text_color: TextColor):
        self.__ENDC = '\033[0m'
        self.Text = text_color + text + self.__ENDC


    
