#!/usr/bin/env python3

import argparse
import os
import re
import shutil


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


def generate_flutter_class(icons: list[tuple[str, str, str]], class_name: str) -> str:
    out = f"""library flutter_tabler_icons;

import 'package:flutter/widgets.dart';

class {class_name} {{
  {class_name}._();

"""
    # Some icons need their names changed to work with Dart variable naming.
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

    for original_name, code_point, font_family in icons:
        name = process_icon_name(original_name, name_adjustments)
        processed_icons[name] = (code_point, font_family)

    # Sort alphabetically
    sorted_names = sorted(processed_icons.keys())

    for name in sorted_names:
        code_point, font_family = processed_icons[name]
        out += f'    static const IconData {name} = IconData(0x{code_point}, fontFamily: "{font_family}", fontPackage: "flutter_tabler_icons");\n'

    out += "\n  static const all = <String, IconData> {\n"

    for name in sorted_names:
        out += f'    "{name}": {name},\n'

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

    # Merge into a single list: (original_name, code_point, font_family)
    all_icons = []

    for name, code_point in outline_icons.items():
        all_icons.append((name, code_point, "tabler-icons"))

    for name, code_point in filled_icons.items():
        all_icons.append((name + "_filled", code_point, "tabler-icons-filled"))

    # Generate single combined class
    combined_class = generate_flutter_class(all_icons, "TablerIcons")

    with open(args.output, "w") as output_file:
        output_file.write(combined_class)

    # Copy TTF files
    ttf_dir = os.path.dirname(args.ttf_out)

    outline_ttf = os.path.join(args.input, "fonts", "tabler-icons.ttf")
    shutil.copy(outline_ttf, args.ttf_out)

    filled_ttf = os.path.join(args.input, "fonts", "tabler-icons-filled.ttf")
    filled_ttf_out = os.path.join(ttf_dir, "tabler-icons-filled.ttf")
    shutil.copy(filled_ttf, filled_ttf_out)
