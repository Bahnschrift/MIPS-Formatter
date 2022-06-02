#!/usr/bin/python3

###############################################################################
# MIPS Assembly Lanuage Formatter                                             #
#                                                                             #
# I bear absolutely no responsibility for any mental damage that occurs as a  #
# result of trying to read the abhorrent mess of spaghetti that is this code. #
#                                                                             #
# It might also be a good idea to output to a specific file instead of        #
# overwriting the original, since I probably coded this in an awful way that  #
# could result in code loss and / or breaking functionality.                  #
#                                                                             #
# If you find any bugs, let my know and if I can bear to try and understand   #
# the code I wrote here enough to fix it, I will.                             #
###############################################################################

import argparse
import subprocess
from pathlib import Path
from formatter import Formatter


# Returns the number of non-whitespace characters in a string
# This is used to (poorly)check for code loss after formatting
def get_num_not_space(s: str) -> int:
    return len(list(filter(lambda c: not c.isspace(), s)))


# Calls "mipsy --check <file>" on the current file
def mipsy_check(f: Path) -> bool:
    checker = subprocess.run(f"mipsy --check {f}", shell=True, capture_output=True)
    if checker.returncode <= 1:
        return not bool(checker.returncode)

    # mipsy not found. Try 1521 mipsy
    assert checker.returncode == 127
    checker = subprocess.run(f"1521 mipsy --check {f}", shell=True, capture_output=True)
    if checker.returncode <= 1:
        return not bool(checker.returncode)

    # 1521 mipsy not found. Ask to continue
    assert checker.returncode == 127
    print("Could not find mipsy. Continuing without valid code could result in code loss.")
    print("Continue anyway? (y/n)", end=" ")
    if input() != "y":
        print("Aborting...")
        exit(1)

    return True


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Format a .s (MIPS assembly language) file")
    argparser.add_argument("input", type=str, help="Input .s file")
    argparser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output .s file. If not specified then input will be overwritten",
    )
    argparser.add_argument(
        "-t",
        "--tab-width",
        type=int,
        default=8,
        help="Number of spaces to use for a tab. Default: 8",
    )

    args = argparser.parse_args()
    input_fpath: Path = Path(args.input)
    output_fpath: Path = Path(args.output) if args.output is not None else input_fpath

    if not input_fpath.exists():
        print(f"Error: {input_fpath} does not exist")
        exit(1)

    valid_code = mipsy_check(input_fpath)
    if not valid_code:
        print("Invalid MIPS Assembly code detected by 'mipsy --check'")
        print("Aborting...")
        exit(1)

    with open(input_fpath) as input_file:
        input_str = input_file.read()
    formatter = Formatter(input_str, tab_width=args.tab_width)

    try:
        output_str = formatter.format()
    except Exception as e:
        # I don't know what could go wrong here, but it's probably quite a lot.
        # If something does, try not to delete all the original code.
        print(f"Unknown error: {e}")
        exit(1)

    input_str_len = get_num_not_space(input_str)
    output_str_len = get_num_not_space(output_str)

    if input_str_len != output_str_len:
        print("Formatted code does not have same length as original. Possible code loss.")
        print("Continue anyway? (y/n)", end=" ")
        if input() != "y":
            print("Aborting...")
            exit(1)

    with open(output_fpath, "w") as output_file:
        output_file.write(output_str)

    print(f"Successfully formatted {input_fpath} to {output_fpath}")
