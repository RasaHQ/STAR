import json
import os
import random

# noinspection PyUnresolvedReferences
from itertools import combinations
from typing import Dict, Text, Any, List, Optional, Tuple, Union


def is_equal_to(value):
    return lambda x: x == value

def is_unequal_to(value):
    return lambda x: x != value

def contains(value):
    return lambda x: value in x

def contains_not(value):
    return lambda x: value not in x

def contains_none_of(value):
    return lambda x: not any([e in x for e in value])

def is_one_of(value):
    return lambda x: x in value


def is_greater_than(value):
    return lambda x: x > value


def is_at_least(value):
    return lambda x: x >= value


def is_less_than(value):
    return lambda x: x < value

def is_at_most(value):
    return lambda x: x <= value


def contain_all_of(value):
    return lambda x: all([e in x for e in value])


def contain_at_least_one_of(value):
    return lambda x: any([e in x for e in value])


def is_not(constraint):
    return lambda x: not constraint(x)


def contains_substring(value):
    return lambda x: value in x


class KnowledgeBaseItem:
    def __init__(self, settings):
        self._id = hash(str(settings))
        self._settings: Dict[Text, Any] = settings

    def __str__(self):
        return str(self._settings)

    def __hash__(self):
        return self._id

    def __eq__(self, other: "KnowledgeBaseItem") -> bool:
        return self._id == other._id

    @property
    def properties(self) -> Dict[Text, Any]:
        return self._settings

    def match(self, constraints: Dict[Text, Any]) -> bool:
        for parameter_name, constraint in constraints.items():
            row_value = self._settings.get(parameter_name)
            if not callable(constraint) and row_value != constraint:
                return False
            elif callable(constraint) and not constraint(row_value):
                return False
        return True


class KnowledgeBaseAPI:
    descriptor_templates = {"General": lambda s: "{}".format(s)}

    def __init__(
        self,
        num_items: int = 1,
        all_parameters: Dict[Text, Any] = None,
        required_parameters: Optional[List[Text]] = None,
    ):
        self._dataset = []
        self.parameters = all_parameters or []
        self.required_parameters = required_parameters or []
        self._generate(num_items)

    def _generate(self, num_items: int) -> None:
        for n in range(num_items):
            self._dataset.append(self._create_random_item(n))

    def add_item(self, item: Dict[Text, Any]) -> None:
        settings = {}
        for parameter in self.parameters:
            print(parameter)
            name = parameter.get("Name")
            if name in item:
                settings.update({name: item[name]})
            else:
                settings.update(self._random_value(parameter, settings))

        self._dataset.append(KnowledgeBaseItem(settings))

    def clear(self):
        self._dataset = []

    def _create_random_item(self, identification_number: int) -> KnowledgeBaseItem:
        # Build the settings by randomly choosing from the options
        # or from the constraints
        settings = {"id": identification_number}
        for parameter in self.parameters:
            settings.update(self._random_value(parameter, settings))

        return KnowledgeBaseItem(settings)

    @staticmethod
    def _random_value(
            parameter: Dict[Text, Any], settings: Dict[Text, Any]
    ) -> Dict[Text, Any]:

        check_enabled = parameter.get("Enabled")
        if callable(check_enabled) and not check_enabled(settings):
            return {}

        if parameter.get("Type") == "Integer":
            _min = parameter.get("Min", 0)
            _max = parameter.get("Max", 100)
            _min = _min(settings) if callable(_min) else _min
            _max = _max(settings) if callable(_max) else _max
            return {parameter["Name"]: random.randint(_min, _max)}
        elif parameter.get("Type") == "Categorical":
            return {parameter["Name"]: random.choice(parameter.get("Categories"))}
        elif parameter.get("Type") == "Boolean":
            return {parameter["Name"]: random.choice([False, True])}
        else:
            raise ValueError(
                f"Unknown parameter type '{parameter.get('Type')}' for parameter '{parameter.get('Name')}'."
            )

    def lookup(self, constraints: Dict[Text, Any]) -> List[KnowledgeBaseItem]:
        self._check_if_required_parameters_provided(constraints)

        return [item for item in self._dataset if item.match(constraints)]

    def get_all(
        self, constraints: Optional[Dict[Text, Any]] = None
    ) -> List[KnowledgeBaseItem]:
        filtered_items = self.lookup(constraints or {})
        return filtered_items

    def sample(
        self, constraints: Optional[Dict[Text, Any]] = None
    ) -> Tuple[Optional[KnowledgeBaseItem], int]:
        filtered_items = self.lookup(constraints or {})
        if filtered_items:
            return random.choice(filtered_items), len(filtered_items)
        else:
            return None, 0

    def _check_if_required_parameters_provided(self, constraints):
        for parameter_name in self.required_parameters:
            if parameter_name not in constraints:
                raise ValueError(
                    f"Parameter '{parameter_name}' is required but was not provided."
                )


def load_db(fn):
    """
    Given a JSON file corresponding to a DB, generate the object
    """
    # print("Loaded DB:", fn)
    parameters = json.load(open(fn))

    # Handle the python expressions in the parameter
    for param in parameters:
        for k, v in param.items():
            if type(v) is str and v[0] == "!":
                param[k] = eval(v[1:])

    return KnowledgeBaseAPI(num_items=100 if 'plane' not in fn else 1000, all_parameters=parameters)


def generic_sample(api, constraints: Optional[Dict[Text, Any]] = None):
    row, count = api.sample(constraints or {})
    if count != 0:
        return row._settings, count
    else:
        raise LookupError("Nothing found for these constraints")


def restaurant_book(restaurant_api, constraints: Dict[Text, Any]):
    name = getval(constraints, 'Name', restaurant_api)

    if constraints["RequestType"] != "Book":
        return {"Message": random.choice(["Available", "Unavailable"]), 'RestaurantName': name}, -1

    outputs = ["Reservation Confirmed", "Reservation Failed"]
    if random.random() > 0.5:
        return {"ReservationStatus": outputs[1], 'RestaurantName': name}, -1
    else:
        return {"ReservationStatus": outputs[0], 'RestaurantName': name}, -1


def hotel_book(hotel_api, constraints: Dict[Text, Any]):
    outputs = ["Reservation Confirmed", "Reservation Failed"]

    name = getval(constraints, 'Name', hotel_api)

    if constraints["RequestType"] != "Book":
        return {"Message": random.choice(["Available", "Unavailable"]), 'HotelName': name}, -1

    if row is None:
        return {"Message": outputs[1], 'HotelName': name}, -1
    else:
        return {"Message": random.choice(outputs), 'HotelName': name}, -1


def hotel_service_request(hotel_api, constraints: Dict[Text, Any]):
    outputs = ["Request Confirmed", "Request Failed"]

    room = getval(constraints, 'RoomNumber', hotel_api)
    time = getval(constraints, 'Time', hotel_api)

    if random.random() < 0.2:
        return {"RequestStatus": outputs[1], 'RoomNumber': room, 'Time': time}, -1
    else:
        return {"RequestStatus": outputs[0], 'RoomNumber': room, 'Time': time}, -1


def plane_search(plane_api, constraints: Dict[Text, Any]):
    row, count = plane_api.sample(dict(constraints))
    return row._settings, count


def plane_book(plane_api, constraints: Dict[Text, Any]):
    plane_id = getval(constraints, 'id', plane_api)

    if constraints["RequestType"] != "Book":
        return {"Message": random.choice(["Available", "Unavailable"]), 'id': plane_id }, -1

    outputs = ["Reservation Confirmed", "Reservation Failed"]
    return {"ReservationStatus": random.choice(outputs), 'id': plane_id }, -1


def trip_directions(trip_api, constraints: Dict[Text, Any]):

    del constraints['DepartureTime']
    del constraints['DepartureLocation']
    del constraints['ArrivalLocation']

    if constraints['TravelMode'] != 'Transit':
      del constraints['Price']

    row, _ = trip_api.sample(constraints)

    d = row._settings

    simple_key = [k for k in d if 'Detail' not in k and 'Instruc' in k][0]
    detail_key = [k for k in d if 'Detail' in k and 'Instruc' in k][0]

    simple = [e for e in d[simple_key] if e[0] != "#"]
    detail = [e[1:] for e in d[simple_key] if e[0] == "#"]

    d[simple_key] = simple
    d[detail_key] = detail

    return d, -1


def ride_book(ride_api, constraints: Dict[Text, Any]):
    if constraints["RequestType"] == "Book":
      return dict(Message="Ride booked."), -1

    query_properties = {
        "DepartureLocation": constraints["DepartureLocation"],
        "ArrivalLocation": constraints["ArrivalLocation"],
        "CustomerName": constraints["CustomerName"]
    }

    del constraints["RequestType"]
    del constraints["DepartureLocation"]
    del constraints["ArrivalLocation"]
    del constraints["CustomerName"]
    row, count = ride_api.sample(constraints)
    if not row:  # ToDo: Do this for all apis
        raise ValueError("Could not find any matching items.")
    settings = row._settings
    settings.update(query_properties)
    return settings, -1


def ride_status(ride_api, constraints: Dict[Text, Any]):
    ride_status_outputs = [
        "Your driver is dropping off another passenger.",
        "Your ride is on its way.",
        "Your driver is arriving.",
    ]
    ride_wait_outputs = [
        "{0} minutes away".format(random.randint(1, 10)) for _ in range(30)
    ]

    return (
        dict(
            RideStatus=random.choice(ride_status_outputs),
            RideWait=random.choice(ride_wait_outputs),
        ),
        -1,
    )

def ride_change(ride_api, constraints: Dict[Text, Any]):
    outputs = [
        "Your trip has been successfully changed.",
        "We are unable to change your trip.",
    ]

    return {"ChangeStatus": random.choice(outputs)}, -1


def bank_balance(bank_api, constraints: Dict[Text, Any]):
    req1 = ['AccountNumber', 'FullName', 'PIN']
    req2 = ['FullName', 'SecurityAnswer1', 'SecurityAnswer2', 'DateOfBirth']
    if not all(e in constraints for e in req1) and not all(e in constraints for e in req2):
      return dict(Message="You must provide either AccountNumber/FullName/PIN or FullName/DateOfBirth/SecurityAnswer1/SecurityAnswer2. We cannot authenticate the user otherwise."), -1

    row, count = bank_api.sample({})
    return row._settings, -1


def bank_fraud_report(bank_api, constraints: Dict[Text, Any]):
    req1 = ['AccountNumber', 'FullName', 'PIN']
    req2 = ['FullName', 'SecurityAnswer1', 'SecurityAnswer2', 'DateOfBirth']
    if not all(e in constraints for e in req1) and not all(e in constraints for e in req2):
      return dict(Message="You must provide either AccountNumber/FullName/PIN or FullName/DateOfBirth/SecurityAnswer1/SecurityAnswer2. We cannot authenticate the user otherwise."), -1

    return {"Confirmation": "Fraud report submitted successfully."}, -1


def shopping_order_item(shopping_api, constraints: Dict[Text, Any]):
    new_constraints = {
        "ItemNumber": constraints["ItemNumber"],
        "ShippingSpeed": contains(constraints["ShippingSpeed"]),
    }

    row, _ = shopping_api.sample(new_constraints)

    if row is None:
        return (
            dict(
                Message="Sorry we were unable to process the order. Please check the item number or the shipping speed."
            ),
            -1,
        )
    else:
        return dict(Message="Order confirmed. Your item will be shipped soon."), -1


def shopping_order_status(null_api, constraints: Dict[Text, Any]):
    outputs = [
        "Your order is being processed. It will be shipped soon.",
        "Your order is on its way.",
        "Your order is arriving soon.",
        "There is a delay in your order.",
    ]

    return dict(Message=random.choice(outputs)), -1

def trivia(null_api, constraints: Dict[Text, Any]):
    questions = [
["A ____ atom in an atomic clock beats 9,192,631,770 times a second", "cesium"],
["A ____ is the blue field behind the stars", "canton"],
["A ____ takes 33 hours to crawl one mile", "snail"],
["A ____ written to celebrate a wedding is called a epithalamium", "poem"],
["A 'sirocco' refers to a type of ____", "wind"],
["A 3 1/2' floppy disk measures ____ & 1/2 inches across", "three"],
["A 300,000 pound wedding dress made of platinum was once exhibited, and in the instructions from the designer was a warning. What was it", "do not iron"],
["A bird in the hand is worth ____", "two in the bush"],
["A block of compressed coal dust used as fuel", "briquette"],
["A blockage in a pipe caused by a trapped bubble of air", "airlock"],
["A blunt thick needle for sewing with thick thread or tape", "bodkin"]
    ]
    q_ind = int(constraints['QuestionNum']) - 1
    row = questions[q_ind]
    return dict(Question=row[0], Answer=row[1]), -1


def meeting_schedule(schedule_api, constraints: Dict[Text, Any]):
    outputs = [
        "Your meeting has been successfuly scheduled.",
        "That person has a conflicting meeting at that time. Try another meeting time."
    ]

    starttime = getval(constraints, 'StartTimeHour', schedule_api)
    endtime = getval(constraints, 'EndTimeHour', schedule_api)
    day = getval(constraints, 'Day', schedule_api)
    name = getval(constraints, 'Name', schedule_api)

    if random.random() > 0.5:
        return dict(Message=outputs[0], StartTime=starttime, EndTime=endtime, Day=day, GuestName=name), -1
    else:
        return dict(Message=outputs[1], StartTime=starttime, EndTime=endtime, Day=day, GuestName=name), -1


def doctor_schedule(
    schedule_api, constraints: Dict[Text, Any]
):
    outputs = [
        "Your appointment has been successfuly scheduled.",
        "The doctor has a conflicting appointment at that time. Try another time or another doctor."
    ]
    
    doctor = getval(constraints, 'Name', schedule_api)
    time = getval(constraints, 'StartTimeHour', schedule_api)

    if constraints["RequestType"] == "Book":
        return dict(Message=outputs[0], DoctorName=doctor, Time=time), -1

    if random.random() > 0.5:
        return {"Message": "The time slot is available.", "DoctorName": doctor, "Time": time}, -1
    else:
        return {"Message": outputs[1], "DoctorName": doctor, "Time": time}, -1


def apartment_schedule(
    schedule_api, constraints: Dict[Text, Any]
):
    outputs = [
        "Your apartment viewing has been successfuly scheduled.",
        "That time is unavailable. Please try another time."
    ]
    if random.random() > 0.5 or constraints["RequestType"] == "Book":
        if constraints["RequestType"] != "Book":
          return {"Message": "The time slot is available."}, -1

        required_items = [
            "Passport",
            "Proof of Income",
            "SCHUFA certificate",
            "Bank Statement",
        ]
        return (
            dict(
                Message=outputs[0]
                + " Please bring {0} and {1} with you.".format(
                    random.choice(required_items), random.choice(required_items)
                )
            ),
            -1,
        )
    else:
        return dict(Message=outputs[1]), -1


def doctor_followup(
    null_api, constraints: Dict[Text, Any]
):
    outputs = [
        "You must take your medicine 2 times a day before meals.",
        "Take your medicine before you go to sleep. If you experience nausea, please contact your doctor immediately.",
    ]

    return dict(Message=random.choice(outputs)), -1


def getval(constraints, key, db):
    """
    Get the value of a constraint
    """
    value = constraints[key]
    if callable(value):
      # find param
      param = [e for e in db.parameters if e['Name'] == key][0]
      if 'Categories' not in param:
        return ''
      
      return [e for e in param['Categories'] if value(e)][0]
    else:
      return value


def party_plan(schedule_api, constraints: Dict[Text, Any]):
    schedule_outputs = [
        "ERROR",
        "The venue is booked at that time. Try another meeting time or another venue."
    ]
    size_outputs = [
        "Your event has been successfully scheduled.",
        "The venue is too small for your party. Try another venue."
    ]

    venue_name = getval(constraints, 'Name', schedule_api)
    day = getval(constraints, 'Day', schedule_api)
    time = getval(constraints, 'StartTimeHour', schedule_api)

    if constraints["RequestType"] == "Book":
      return dict(Message=size_outputs[0], VenueName=venue_name, Day=day, Time=time), -1

    if random.random() < 0.1:
        return dict(Message=schedule_outputs[1], VenueName=venue_name, Day=day, Time=time), -1
    elif random.random() > 0.1:
        return dict(Message="The venue is available.", VenueName=venue_name, Day=day, Time=time), -1
    else:
        return dict(Message=size_outputs[1], VenueName=venue_name, Day=day, Time=time), -1


def party_rsvp(schedule_api, constraints: Dict[Text, Any]):
    return dict(Message="Thank you for your RSVP. See you there."), -1


def spaceship_access_codes(null_api, constraints: Dict[Text, Any]):
    outputs = [
        "The door is now unlocked.",
        "Sorry, you are not authorized to unlock the door. Please obtain a clearance code from the Captain.",
    ]

    if (
        constraints["UserRank"] in ["Chief Engineer", "Bartender"]
        and constraints["CodeType"] != "Clearance"
    ):
        return dict(Message=outputs[1]), -1
    else:
        return dict(Message=outputs[0]), -1


def spaceship_life_support(null_api, constraints: Dict[Text, Any]):
    outputs = ["Successful! Door opened"]
    return dict(Message=outputs[0]), -1


dbs = {"null": None}


def load_databases() -> None:
    # Load all DBs
    global dbs
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbs")
    print(f"Loading databases from '{db_dir}'.")
    for filename in os.listdir(db_dir):
        if filename[0] == ".":
            continue
        db_name = os.path.splitext(filename)[0]
        # print(f"loading {db_name}")
        dbs[db_name] = load_db(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "dbs", filename)
        )


def constraint_and(constraint1, constraint2):
    return lambda x: constraint1(x) and constraint2(x)


def constraint_list_to_dict(constraints: List[Dict[Text, Any]]) -> Dict[Text, Any]:
    result = {}
    for constraint in constraints:
        for name, constraint_function in constraint.items():
            if name not in result:
                result[name] = constraint_function
            else:
                result[name] = constraint_and(result[name], constraint_function)
    return result


def call_api(api_name, constraints: List[Dict[Text, Any]]) -> Tuple[Dict[Text, Any], int]:
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "apis", api_name + ".json"
        ),
        "r"
    ) as file:
        api_schema = json.load(file)
    api_fn = eval(api_schema["function"])
    api_obj = dbs[api_schema["db"]]

    if constraints:
        all_provided_parameters = set.union(*[set(c) for c in constraints])
    else:
        all_provided_parameters = set()

    for parameter in api_schema["required"]:
        if parameter not in all_provided_parameters:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    res, count = api_fn(api_obj, constraint_list_to_dict(constraints))
    if res:
        res["api_name"] = api_name  # To track where the KB item came from; not shown in front end
    if api_schema["returns_count"]:
        return res, count
    else:
        return res, -1


load_databases()
