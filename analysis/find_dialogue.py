
import json
import os
from typing import Any, Dict, List, Optional, Text
from utils import file_system_scan


def is_labeled_happy(dialogue_data: Dict[Text, Any]) -> bool:
  return dialogue_data["Scenario"]["Happy"]


def is_labeled_unhappy(dialogue_data: Dict[Text, Any]) -> bool:
  return not dialogue_data["Scenario"]["Happy"]


def is_labeled_multitask(dialogue_data: Dict[Text, Any]) -> bool:
  return dialogue_data["Scenario"]["MultiTask"]


def includes_task(task: Text) -> callable:
  def test(dialogue_data: Dict[Text, Any]) -> bool:
    tasks = [capability["Task"] for capability in dialogue_data["Scenario"]["WizardCapabilities"]]
    return task in tasks
  return test


def calls_api_for(task: Text) -> callable:
  def test(dialogue_data: Dict[Text, Any]) -> bool:
    tasks = set()
    for event in dialogue_data["Events"]:
      if event["Agent"] == "KnowledgeBase":
        tasks.add(event["APIName"])
    return task in tasks
  return test


def wizard_reports_unsure(dialogue_data: Dict[Text, Any]) -> bool:
  if not "WizardQuestionnaire" in dialogue_data.keys():
    return False
  for report in dialogue_data["WizardQuestionnaire"]:
    question: Text = report["Question"]
    if question.startswith("Where you unsure about what to do at any time?"):
      return report["Answer"]
  return False


def _not(f: callable) -> callable:
  return lambda x: not f(x)


def find_dialogues(
  directory: Text,
  tests: List[callable],
  max_items: Optional[int] = None,
) -> List[Text]:
  dialogues = []

  def run_test(filename: Text) -> None:
    nonlocal dialogues
    with open(filename, "r") as stream:
      data = json.load(stream)
    for test in tests:
      if not test(data):
        return
    dialogues.append(filename)

  file_system_scan(run_test, directory)

  if max_items is not None and max_items < len(dialogues):
    return dialogues[:max_items]
  else:
    return dialogues


if __name__ == "__main__":
  # result = find_dialogues(
  #   "dialogues", 
  #   [
  #     wizard_reports_unsure, 
  #     _not(is_labeled_multitask),
  #   ]
  # )
  result = find_dialogues(
    "dialogues", 
    [
      includes_task("restaurant_book"),
      _not(calls_api_for("restaurant_book")),
      is_labeled_happy
    ]
  )
  print(result)
