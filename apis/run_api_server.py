
from collections import defaultdict

from flask import Flask, json, jsonify

import api

flask = Flask(__name__)

MOCK_DATA_HEAP = defaultdict(list)


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


@flask.route("/<task>/<constraints_description>", methods=["GET"])
def retrieve(task, constraints_description):

  if MOCK_DATA_HEAP.get(task):
    return MOCK_DATA_HEAP[task].pop(0)

  try:
    constraints = json.loads(constraints_description)
  except Exception as e:
    raise InvalidUsage("Bad constraints string")

  try:
    item, num_other_items = api.call_api(
      task, 
      constraints=constraints,
    )
    return json.dumps({"Message": "Ok", "Item": item, "NumOtherItems": num_other_items})
  except Exception as e:
    raise InvalidUsage("API code failed")


@flask.route("/mock/<task>/<response>", methods=["GET"])
def mock(task, response):
  """Add responses to the MOCK_DATA_HEAP"""

  MOCK_DATA_HEAP[task].append(response)
  return ""


if __name__ == '__main__':
    flask.run()
