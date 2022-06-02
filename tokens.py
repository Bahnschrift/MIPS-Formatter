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
        self.has_newline = False

    def __str__(self):
        if self.has_newline:
            return f"\t.{self.name}\n\t\t{' '.join(self.params)}"
        else:
            return f"\t.{self.name}\t{' '.join(self.params)}"

    def add_param(self, param: str):
        self.params.append(param)


# Just a newline.
class NewLine(Token):
    def __str__(self):
        return "\n"
