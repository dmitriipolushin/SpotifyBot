import json
from main import get_information


def test_get_information_type():
    f = open('item_test.json')
    item = json.load(f)
    assert isinstance(get_information(item), dict)
