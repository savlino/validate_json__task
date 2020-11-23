"""
Following script allows to check events using prvided schemes and returns
html report with details and instructions on each found error.
Events and schemas should be placed to folders "event" and "schema" respectively.
Module "jsonschema" requires to run this script.
"""

import os
import json
from jsonschema.exceptions import SchemaError
from jsonschema import Draft7Validator


def validate_json(record, fitting_schema):
    # defines procedure to validate given json entry
    validator = Draft7Validator(fitting_schema)
    errors = sorted(validator.iter_errors(record), key=lambda e: e.path)

    if len(errors):
        report_extender("<ul><h5>Value errors:</h5>")
        for error in errors:
            report_extender(string_formatter(error))
        report_extender("</ul>")
    else:
        report_extender("<ul><b>No errors found</b></ul>")


def json_list_handler(json_arr):
    # handles process of traversing through given event list
    for ent in json_arr:
        report_extender(
            f"<h4>{os.listdir('./event')[json_arr.index(ent)]}</h4>"
        )
        report_printer(ent)


def report_printer(entry):
    # handles process of creating top layer of report and calling validation
    try:
        if entry["data"] == None:
            report_extender(f"<ul><b>No entries found</b></ul>")
        elif entry["event"] in schem_dir.keys():
            validate_json(entry["data"], schem_dir[entry["event"]])
            Draft7Validator.check_schema(schem_dir[entry["event"]])
        elif entry["event"].replace(" ", "") in schem_dir.keys():
            report_extender(
                "<ul><h5>JSON errors:</h5>\
                 <li>Incorrect event name format</li></ul>"
            )
            validate_json(
                entry["data"], schem_dir[entry["event"].replace(" ", "")]
            )
            Draft7Validator.check_schema(
                schem_dir[entry["event"].replace(" ", "")]
            )
        else:
            report_extender(
                f"<ul>Schema for <u>{entry['event']}</u> not \
                  found, unable to confirm</ul>"
            )
    except (TypeError, KeyError):
        report_extender(f"<ul><b>Empty entry</b></ul>")
    except SchemaError:
        report_extender(
            f"<ul><b>Schema for <u>{entry['event']}</u> is broken, \
            unable to confirm</b></ul>"
        )


def report_extender(line):
    #handles extending report by single line
    global report_to_exp
    report_to_exp += line


def string_formatter(single_error):
    # translates error messages to user readable format
    msg = single_error.message
    rel_path = single_error.relative_path

    if "required property" in msg and "type" in msg:
        return f"<li>Unspecified {msg.split()[0]} in \
                 '{single_error.absolute_path[0]}', record number \
                 {single_error.absolute_path[1]}</li>"
    elif "required property" in msg:
        return f"<li>Fill in {msg.split()[0]} field</li>"
    elif single_error.instance == None:
        return f"<li>Fill in '{rel_path[-1]}' field</li>"
    elif "is not of type" in msg and rel_path:
        return f"<li>Change type of '{rel_path[-1]}' equals \
                 <u>{single_error.instance}</u> inside '{rel_path[0]}' \
                 field to type '{single_error.validator_value}'</li>"
    else:
        return f"<li>{msg}\n</li>"


json_list = []
schem_dir = {}
report_to_exp = "<h4>Issues found</h4>"

if __name__ == "__main__":
    for entry in os.listdir("./event"):
        with open("./event/" + entry) as file:
            json_list.append(json.load(file))

    for sch_entry in os.listdir("./schema"):
        with open("./schema/" + sch_entry) as file:
            schem_dir[sch_entry.split(".")[0]] = json.load(file)

    json_list_handler(json_list)

    with open("README.html", "w") as file:
        file.write(report_to_exp)
