
import api

if __name__ == "__main__":

    print()
    
    print("Search for a trivia question")
    item, num_other_items = api.call_api(
        "trivia",
        constraints=[{
            "QuestionNum": 2
        }],
    )
    print(item)
    print(num_other_items)
    print()

    print("Search for an apartment")
    item, num_other_items = api.call_api(
        "apartment_search", 
        constraints=[
            {"HasBalcony": True},
            {"NumRooms": api.is_greater_than(2)},
            {"NumRooms": api.is_less_than(5)}
        ],
    )
    print(item)
    print(num_other_items)
