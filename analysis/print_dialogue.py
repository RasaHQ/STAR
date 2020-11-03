
"""

...

"""


from typing import Text, Dict, Set, List, Any, Optional
import json
import os
import re
from copy import deepcopy
from collections import defaultdict
from numpy import mean
from termcolor import colored
import sys
from utils import file_system_scan


FREE_FORM = "free_form"

WIZARD_COLOR = "red"
USER_COLOR = "green"
API_COLOR = "cyan"
GUIDE_COLOR = "yellow"



def print_dialogue(filename: Text) -> None:
  print()
  print(filename)
  print()
  with open(filename, "r", encoding="utf-8") as file:
    dialogue = json.load(file)

  for event in dialogue["Events"]:
    label = None
    if event["Agent"] == "Wizard" and "Text" in event and event["Action"] == "pick_suggestion":
      print(colored(f"WIZ [{event['ActionLabel']}]: {event['Text']}", WIZARD_COLOR))
    elif event["Agent"] == "Wizard" and "Text" in event and event["Action"] == "utter":
      print(colored(f"WIZ [{FREE_FORM}]: {event['Text']}", WIZARD_COLOR))
    elif event["Agent"] == "User" and "Text" in event:
      print(colored(f"USR: {event['Text']}", USER_COLOR))
    elif event["Agent"] == "KnowledgeBase" and "Item" in event:
      print(colored(f"API: {event['Item']}", API_COLOR))
    elif event["Agent"] == "UserGuide":
      print(colored(f"GUIDE: {event['Text']}", GUIDE_COLOR))


if __name__ == "__main__":
  dialogue_number = sys.argv[1] if len(sys.argv) >= 1 else 1
  print_dialogue(f"dialogues/{dialogue_number}.json")
