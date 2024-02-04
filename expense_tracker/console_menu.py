from typing import Callable,Any
import logging

logger = logging.getLogger('console_menu')

def handle_input_defaults(input:str):
    """
    Meant to handle the input as soon as it's received. Takes care of exit sequences and help. 
    Returns:
    - False if nothing entered
    - True if exit message received
    - None if asking for help
    """
    if input == "": 
        return False
    if input.lower() == "exit":
        return True
    if input[-1] == "?":
        return None
    
    return ""

class Menu():
    name: str
    description: str
    items: list['MenuEntry|Menu']
    
    def display(self, breadcrumbs: list):
        print()
        print(*breadcrumbs,sep=" > ")
        print(f"## {self.name} ##")
        print()
        if self.description != "":
            print(self.description)

        for n,item in enumerate(self.items):
            print(f" > {n+1}. {item.name}")

    def get_choice_help(self, input_str) -> str:
        """
        Returns the text that should display when prompting for help.
        """
        choice_value = input_str[:-1]
        valid,err = self.validate_choice(choice_value)

        if valid:
            choice_obj = self.items[int(choice_value)-1]

            if type(choice_obj) is Menu:
                return "No help text for a menu. Type in the number and press enter to open that menu."
            if type(choice_obj) is MenuEntry:
                return choice_obj.description

        if choice_value == "":
            return "Help: Enter the number preceding the action you would like to perform and press enter. You can type 'exit' at any time to exit out of the menu entirely. You can press enter, without typing anything in, to return to the previous menu."
        else:
            return f"Could not get help text because the number preceding the '?' is invalid: {err}"

    def validate_choice(self, choice) -> tuple[bool,str]:
        try:
            choice = int(choice)
        except ValueError:
            return (False, "Invalid Choice. Type in the number of the menu choice you would like to select and press Enter.")
        
        available_choices = {
            "choices": [*range(1,len(self.items)+1)],
            "name": [item.name for item in self.items]
            }

        if choice < 1:
            return (False, f"Invalid Choice. Number must be 1 or more. Available choices {available_choices['choices']}")

        if choice > len(self.items):
            return (False, f"Invalid Choice. Number must be from the menu. Available choices {available_choices['choices']}")
        
        return (True, self.items[choice-1].name)

    def run(self, exit_menu = False, breadcrumbs:list|None = None, carryover_text: 'str|list[str]' = ""):
        input_str = None
        if breadcrumbs is None:
            breadcrumbs = [self.name]

        # Receive input
        while not exit_menu:
            self.display(breadcrumbs)

            if len(carryover_text) > 0:
                if type(carryover_text) is list:
                    for msg in carryover_text:
                        print(msg)
                else:
                    print(carryover_text)
                
                carryover_text = ""

            input_str = input("Choice: ")

            exit_code = handle_input_defaults(input_str)
            match exit_code:
                case False:
                    # returning False exits the current menu and goes to the previous one
                    if len(breadcrumbs) > 0:
                        breadcrumbs.pop()

                    return (False, breadcrumbs)
                case True:
                    # Exit if exit command is given
                    # returning True exits the program
                    return (True, None)
                case None:
                    carryover_text = self.get_choice_help(input_str)
                    continue

            # Validate input against the available menu items
            valid,err = self.validate_choice(input_str)
            if not valid:
                carryover_text = err
                continue

            choice = self.items[int(input_str)-1]

            if type(choice) is Menu:
                breadcrumbs.append(choice.name)
                exit_menu, breadcrumbs = choice.run(exit_menu, breadcrumbs=breadcrumbs)
            else:
                print(choice.name)
                if callable(choice.exit_action):
                    _ =choice.exit_action(**choice.exit_action_args)

                    # Handle the return value of the choice. 
                    ## The choice can return a list of strings that should be added onto the carryover text. 
                    if type(_) is list:
                        if carryover_text == "": 
                            carryover_text = _
                            continue

                        if type(carryover_text) is list:
                            carryover_text += _
                            continue

                        # At this point, carryover_text must be a string with something in it. 
                        carryover_text = [carryover_text]
                        carryover_text += _
                        continue

                    if _ is True:
                        return (True, None)
                else:
                    logger.debug("Returning the value from MenuEntry. Not calling a function")
                    return (False, choice.exit_action)


    

    def __init__(self, name, items, description="") -> None:
        self.name = name
        self.items = items
        self.description = description

class MenuEntry():
    name: str
    description: str
    exit_action: Callable|Any
    exit_action_args: dict

    def __init__(self, name, description, func, args={}) -> None:
        self.name = name
        self.description = description
        self.exit_action = func
        self.exit_action_args=args