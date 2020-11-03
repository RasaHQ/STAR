
import os
import re
from typing import Any, List, Text

from numpy import mean


def file_system_scan(f: Any, dir_name: Text, file_extension: Text = ""):
  for root, dirs, files in os.walk(dir_name):
    for file in files:
      if (not file_extension) or re.match(file_extension, file):
        f(os.path.join(root, file))


def get_tasks() -> List[Text]:
  return [os.path.basename(x[0]) for x in os.walk("tasks")][1:]
