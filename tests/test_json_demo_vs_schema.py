
from jsonschema import validate
import json

from chemmd import SCHEMA


with open(SCHEMA) as json_file:
    json_schema = json.load(json_file)


def test_sipos_nmr_json_schema(sipos_nmr_json):
    assert validate(sipos_nmr_json, json_schema) is None


def test_sipos_nmr2_json_schema(sipos_nmr2_json):
    assert validate(sipos_nmr2_json, json_schema) is None


def test_ernesto_nmr_schema(ernesto_nmr):
    assert validate(ernesto_nmr, json_schema) is None
