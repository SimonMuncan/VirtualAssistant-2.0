from assistantGUI import *
import re, ast

class CommandStrategy:
    def execute(self,main_window, command):
        pass
    
    # Strategy for showing the weather page
class ShowWeatherPage(CommandStrategy):
    def execute(self,main_window, command):
        # Regular expression pattern for matching the command
        pattern = re.compile("show weather",re.IGNORECASE) 
        if pattern.match(command):
            main_window.assistantResponse(f"Showing weather page")
            main_window.succSound()
            main_window.weatherPage()
            