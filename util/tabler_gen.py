#!/usr/bin/env python3

import argparse
import os
import re
import shutil


# def get_icon_locations(input: str):
#     parser = tinycss.make_parser("page3")
#     stylesheet = parser.parse_stylesheet(input)

#     for rule in stylesheet.rules:
#         for selector in rule.selector:
#             if selector.value == "before":
#                 icon_name = rule.selector[1].value
#                 icon_location = rule.declarations[0].value[0].value

#                 print(icon_name)
#                 print(icon_location)
#                 print(type(icon_location))
#                 print(len(icon_location))

# Converts the given string to camel case. This isn't a complete implementation,
# and is only applicable for converting icon names.
# https://www.geeksforgeeks.org/python-convert-snake-case-string-to-camel-case/


# Converts the given string to camel case. This isn't a complete implementation,
# and is only applicable for converting icon names.
# https://www.geeksforgeeks.org/python-convert-snake-case-string-to-camel-case/
def process_icon_name(icon: str, name_adjustments: dict) -> str:
    name = icon.replace("-", "_")

    for name_adjustment in name_adjustments:
        if name.startswith(name_adjustment):
            name = name.replace(
                name_adjustment, name_adjustments[name_adjustment], 1
            )

    if name == "switch":
        name = "switch_"

    return name


# Generates a Flutter class from the given dict of names and code points.
# Largely taken from
# https://github.com/ScerIO/icon_font_generator/blob/master/lib/generate_flutter_class.dart
def generate_flutter_class(name_code_point_dict: dict[str, str], class_name: str, font_family: str) -> str:
    out = f"""library flutter_tabler_icons;

import 'package:flutter/widgets.dart';

class {class_name} {{
  {class_name}._();

"""
    # Some icons need their names changed to work with Dart variable naming.
    # https://github.com/fluttercommunity/font_awesome_flutter/blob/5e8020d8bfce95568498e58b8d458c781ec50de1/util/lib/main.dart#L17
    name_adjustments = {
        "500px": "fiveHundredPx",
        "360-degrees": "threeHundredSixtyDegrees",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "0": "zero",
        "42-group": "fortyTwoGroup",
        "00": "zeroZero",
        "100": "hundred",
    }

    processed_icons = {}

    for icon in name_code_point_dict:
        name = process_icon_name(icon, name_adjustments)
        processed_icons[name] = name_code_point_dict[icon]

        code_point = name_code_point_dict[icon]

        out += f'    static const IconData {name} = IconData(0x{code_point}, fontFamily: "{font_family}", fontPackage: "flutter_tabler_icons");\n'

    out += "\n  static const all = <String, IconData> {\n"

    for icon in processed_icons:
        out += f'    "{icon}": {icon},\n'

    out += "  };\n}\n"

    return out


def parse_css(css_file_path: str) -> dict[str, str]:
    name_code_point_dict = {}

    with open(css_file_path, "r") as input_file:
        css = input_file.read()
        rules = re.findall(r".*:before {\s.*\s}", css)

        for rule in rules:
            name = re.search(r"(?<=\.ti-).*(?=:)", rule).group()
            code_point = re.search(r'(?<=content: "\\).*(?=";)', rule).group()

            name_code_point_dict[name] = code_point

    return name_code_point_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        help="Tabler Fonts directory",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file for the Dart class",
        required=True,
    )

    parser.add_argument(
        "-to",
        "--ttf-out",
        help="Where to copy the TTF file",
        required=True,
    )

    args = parser.parse_args()

    # Parse outline icons
    outline_css_path = os.path.join(args.input, "tabler-icons.css")
    outline_icons = parse_css(outline_css_path)

    # Parse filled icons
    filled_css_path = os.path.join(args.input, "tabler-icons-filled.css")
    filled_icons = parse_css(filled_css_path)

    # Generate outline class
    outline_class = generate_flutter_class(outline_icons, "TablerIcons", "tabler-icons")

    with open(args.output, "w") as output_file:
        output_file.write(outline_class)

    # Generate filled class
    filled_output = args.output.replace(".dart", "_filled.dart")
    filled_class = generate_flutter_class(filled_icons, "TablerIconsFilled", "tabler-icons-filled")

    with open(filled_output, "w") as output_file:
        output_file.write(filled_class)

    # Copy TTF files
    ttf_dir = os.path.dirname(args.ttf_out)

    outline_ttf = os.path.join(args.input, "fonts", "tabler-icons.ttf")
    shutil.copy(outline_ttf, args.ttf_out)

    filled_ttf = os.path.join(args.input, "fonts", "tabler-icons-filled.ttf")
    filled_ttf_out = os.path.join(ttf_dir, "tabler-icons-filled.ttf")
    shutil.copy(filled_ttf, filled_ttf_out)
