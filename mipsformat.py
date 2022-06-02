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
from math import ceil

# So the basic idea of this is that the input code is parsed character by character and divided up into a list of
# 'terms', which are then grouped into 'tokens'.
# A token is either a Label, a Directive, a Instruction, Comment, or NewLine.
# Tokens implement the .__str__() method to return exactly how they should be formatted in the output.
# For example, instructions should always be indented once (https://jashankj.space/notes/cse-comp1521-better-assembly/),
# so the .__str__() method of Instructions always prepends a tab character.
#
# This 'Token' class is pretty much just for typing.
class Token:
    def __init__(self):
        pass


# Labels are terms that end with a colon.
class Label(Token):
    def __init__(self, label):
        self.label: str = label

    def __str__(self):
        return f"{self.label}:"


# Instructions consist of an 'operator' and a list of operands.
class Instruction(Token):
    def __init__(self, operator: str):
        self.operator: str = operator
        self.operands: list[str] = []

    def __str__(self):
        if len(self.operands) == 0:
            return f"\t{self.operator}"

        return f"\t{self.operator}\t{', '.join(self.operands)}"

    def add_operand(self, operand: str):
        self.operands.append(operand)


# Comments begin with a '#' and are terminated by a newline.
class Comment(Token):
    def __init__(self):
        self.comment: str = ""
        self.indentation: int = 0

    def __str__(self):
        return "\t" * self.indentation + f"#{self.comment}"

    def add_char(self, char: str):
        self.comment += char


# Directives are terms that begin with a '.'.
class Directive(Token):
    def __init__(self, section_name: str):
        self.name: str = section_name
        self.params: list[str] = []

    def __str__(self):
        return f"\t.{self.name}\t{' '.join(self.params)}"

    def add_param(self, param: str):
        self.params.append(param)


# Just a newline.
class NewLine(Token):
    def __str__(self):
        return "\n"


# A block is a list of tokens.
# A block will only ever contain a single label.
# The purpose of a block is to align comments within a section, or 'block' of code.
class Block:
    def __init__(self, tab_width):
        self.tokens: list[Token] = []
        self.tab_width = tab_width

    def add_token(self, token: Token):
        self.tokens.append(token)

    # Indents all comments to a consistent level
    def align_comments(self) -> None:
        comment_col = self.find_comment_column()
        # Align all comments on the same line as other code to the same level
        for i, token in enumerate(self.tokens):
            if isinstance(token, Comment):
                if i > 1 and isinstance(instruction := self.tokens[i - 1], Instruction):
                    instruction_length = self.instruction_length(instruction)
                    # I think this formula is wrong
                    # TODO: Fix
                    token.indentation = ceil((comment_col - instruction_length) / self.tab_width)
                else:
                    token.indentation = 1

        # Do not any comments at the end of a block, since they are like in actuality descriptions of the next block
        for i, token in enumerate(reversed_tokens := self.tokens[::-1]):
            if (
                isinstance(token, Comment)
                and i < len(reversed_tokens) - 1
                and isinstance(reversed_tokens[i + 1], NewLine)
            ):
                token.indentation = 0
            elif not isinstance(token, NewLine):
                break

    # Returns the correct column to place comments in so that they are all aligned
    def find_comment_column(self) -> int:
        comment_col = 0
        for token in self.tokens:
            if isinstance(token, Instruction):
                instruction_length = self.instruction_length(token)
                comment_col = max(
                    comment_col, instruction_length + self.tab_width - (instruction_length % self.tab_width)
                )
        return comment_col

    # Returns the string length of an instruction, accounting for variable tab widths
    def instruction_length(self, instruction: Instruction) -> int:
        length = self.tab_width  # Tab before operator
        length += self.tab_width  # Operator + distance until first operand
        length += sum(map(len, instruction.operands)) + 2 * (len(instruction.operands) - 1)  # Operands
        return length


# To anyone who reads this: I am sorry.
# There's really no good reason for this to be a class, but y'know. It's Python...
class Formatter:
    def __init__(self, input_str: str, tab_width: int = 8):
        self.input_str = input_str
        if self.input_str[-1] != "\n":
            self.input_str += "\n"

        self.tab_width = tab_width

    # Formats the input code and returns it as a string
    def format(self) -> str:
        self.tokens = []
        self.tokenize()
        parsed_str: str = "".join(map(str, self.tokens)) + "\n"
        return parsed_str

    def tokenize(self) -> None:
        i = 0
        block: Block = Block(self.tab_width)  # The current block of code, used to align comments
        instruction: Instruction | None = None  # The current instruction being built that new operands are added to
        directive: Directive | None = None  # The current directive being built that new parameters are added to
        started = False  # Flag that keeps that is True once the first non-comment or newline token

        while i < len(self.input_str):
            # Comment
            if self.input_str[i] == "#":
                # Comments mean the end of Instructions
                if instruction is not None:
                    block.add_token(instruction)
                    self.tokens.append(instruction)
                    instruction = None

                comment, i = self.get_comment(i + 1)
                if started:
                    block.add_token(comment)
                self.tokens.append(comment)

            # NewLine
            elif self.input_str[i] == "\n":
                # NewLines also mean the end of Instructions
                if instruction is not None:
                    block.add_token(instruction)
                    self.tokens.append(instruction)
                    instruction = None

                i += 1

                # Only have a single newline after a label. Come to think of it, this would break if there were a
                # comment on the same line as the label.
                # TODO: Fix
                if (
                    len(self.tokens) >= 2
                    and isinstance(self.tokens[-2], Label)
                    and isinstance(self.tokens[-1], NewLine)
                ):
                    continue

                # Don't allow 2 empty lines (i.e. 3 newline tokens) in a row
                if len(self.tokens) >= 2 and all(isinstance(token, NewLine) for token in self.tokens[-2:]):
                    continue

                block.add_token(NewLine())
                self.tokens.append(NewLine())

            # Ignore whitespace. This is *probably* fine
            # I think I had a good reason for not using .isspace() here, but I've forgotten it...
            # Maybe carriage return line endings will break here? Not sure how they are handled with Python
            elif self.input_str[i] in [" ", "\t"]:
                i += 1

            elif not self.input_str[i].isspace():
                started = True
                term, i = self.get_term(i)

                # Labels
                if term.endswith(":"):
                    block.align_comments()
                    block = Block(self.tab_width)
                    self.tokens.append(Label(term[:-1]))
                    self.tokens.append(NewLine())  # Headers are followed by a newline

                # Directives
                # TODO: This needs more work to better format terms following directives
                elif term.startswith("."):
                    directive = Directive(term[1:])
                    self.tokens.append(directive)

                # Operators
                elif instruction is None:
                    instruction = Instruction(term)

                # Operands
                else:
                    if term.endswith(","):
                        term = term[:-1]
                    instruction.add_operand(term)

            else:
                # This should be impossible to reach. I think this is just from earlier, but I'm going to leave it in.
                print(f"Error: unknown symbol {self.input_str[i]} at index {i}")
                raise ValueError

        block.align_comments()

    # Reads in characters and adds them to the Comment object until a newline is reached
    # Returns the Comment object and the index of the character after the comment
    def get_comment(self, i: int):
        comment = Comment()
        while self.input_str[i] != "\n":
            comment.add_char(self.input_str[i])
            i += 1
        return comment, i

    # Reads in the next term and returns it along with index of the character after the term
    def get_term(self, i: int):
        term = ""

        # Though terms are usually space separated, strings should be treated as a single term
        if self.input_str[i] == '"':
            term += '"'
            i += 1
            # This probably doesn't cover all cases
            # TODO: Make better
            while not (self.input_str[i] == '"' and self.input_str[i - 1] != "\\"):
                term += self.input_str[i]
                i += 1
            term += '"'
            i += 1

        else:
            while not self.input_str[i].isspace():
                term += self.input_str[i]
                i += 1

        return term, i


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
