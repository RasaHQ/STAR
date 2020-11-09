
from collections import defaultdict
from typing import Any, Dict, List, Text

from flask import Flask, json, jsonify, request

import api

flask = Flask(__name__)

MOCK_DATA_HEAP = defaultdict(list)

Constraint = List[Dict[Text, Any]]


class InvalidUsage(Exception):
  def __init__(self, message, status_code=None):
    Exception.__init__(self)
    self.message = message
    self.status_code = status_code or 400

  def to_dict(self):
    return {"Message": self.message}


@flask.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response


def convert_comparators(constraints: List[Constraint]) -> List[Constraint]:
  converted_constraints = []
  for constraint in constraints:
    slot = constraint.get("Slot")
    value = constraint.get("Value")
    comparator = constraint.get("Comparator")
    if not comparator:
      converted_constraints.append({slot: value})
    else:
      converted_constraints.append({slot: eval(f"api.{comparator}({value})")})
  return converted_constraints


@flask.route("/<task>", methods=["POST"])
def retrieve(task):
  if MOCK_DATA_HEAP.get(task):
    return MOCK_DATA_HEAP[task].pop(0)

  try:
    constraints = request.get_json(silent=True)
    constraints = convert_comparators(constraints)
  except Exception as e:
    raise InvalidUsage("Bad constraints string")

  try:
    item, num_other_items = api.call_api(
      task, 
      constraints=constraints,
    )
    return jsonify({"Message": "Ok", "Item": item, "NumOtherItems": num_other_items})
  except Exception as e:
    raise InvalidUsage("API code failed")


@flask.route("/mock/<task>/<response>", methods=["GET"])
def mock(task, response):
  """Add responses to the MOCK_DATA_HEAP"""

  MOCK_DATA_HEAP[task].append(response)
  return ""


@flask.route("/mock/clear", methods=["GET"])
def mock_clear():
  """Clear MOCK_DATA_HEAP"""

  MOCK_DATA_HEAP.clear()
  return ""


if __name__ == '__main__':
    flask.run()
