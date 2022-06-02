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

# TODO: Refactor everything

import argparse
from formatter import Formatter


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Format a .s (MIPS assembly language) file")
    argparser.add_argument("input", type=argparse.FileType("r+"), help="Input .s file")
    argparser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w+"),
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

    input_str = args.input.read()
    formatter = Formatter(input_str, tab_width=args.tab_width)

    # TODO: Run "mipsy --check [file]" before formatting to make sure the input is actual valid MIPS code

    try:
        formatted = formatter.format()
    except Exception as e:
        # I don't know what could go wrong here, but it's probably quite a lot.
        # If something does, try not to delete all the original code.
        print("Error. Sorry...")
        formatted = input_str

    if args.output is not None:
        args.output.write(formatted)
        args.output.close()
    else:
        args.input.seek(0)
        args.input.write(formatted)
        args.input.truncate()

    args.input.close()
