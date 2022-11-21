import json
from main import get_information
from main import get_iq_articles


def test_get_information_type():
    f = open('item_test.json')
    item = json.load(f)
    assert isinstance(get_information(item), dict)


def test_get_iq_articles_error():
    try:
        get_iq_articles('test')
        assert False
    except Exception:
        assert True
