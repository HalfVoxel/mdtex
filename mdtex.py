#!/usr/bin/env python3

import sys
from itertools import takewhile
from subprocess import call
import os
import re
import shutil


class Que:
    '''Simple wrapper around an iterator to provide peek and prev methods'''

    def __init__(self, stream):
        self.stream = stream
        self.last_token = None
        self.prev_token = None
        self.peek_token = None

    def prev(self):
        return self.prev_token

    def next(self):
        self.prev_token = self.last_token
        self.last_token = self.peek()
        self.peek_token = None
        return self.last_token

    def peek(self):
        if self.peek_token is not None:
            return self.peek_token

        self.peek_token = next(self.stream, None)
        return self.peek_token


def process(input):
    keywords = {"arccos",
                "arccot",
                "arcsin",
                "arctan",
                "cos",
                "cosh",
                "cot",
                "coth",
                "csc",
                "sec",
                "sin",
                "sinh",
                "tan",
                "tanh",
                "arg",
                "sqrt",

                # lowercase greek alphabet
                "alpha",
                "beta",
                "gamma",
                "delta",
                "epsilon",
                "zeta",
                "eta",
                "theta",
                "iota",
                "kappa",
                "lambda",
                "mu",
                "nu",
                "xi",
                "omicron",
                "pi",
                "rho",
                "sigma",
                "tau",
                "upsilon",
                "phi",
                "chi",
                "psi",
                "omega",

                # Uppercase greek alphabet
                "Alpha",
                "Beta",
                "Gamma",
                "Delta",
                "Epsilon",
                "Zeta",
                "Eta",
                "Theta",
                "Iota",
                "Kappa",
                "Lambda",
                "Mu",
                "Nu",
                "Xi",
                "Omicron",
                "Pi",
                "Rho",
                "Sigma",
                "Tau",
                "Upsilon",
                "Phi",
                "Chi",
                "Psi",
                "Omega"
                }

    token_first = {'#', '$', '*', '\n', '(', ')', '[', ']', '\\'}

    def consume_single_spaces(que):
        while que.peek() is not None and que.peek() == " ":
            que.next()

    def tokenize(iterator):
        ''' Generator function for tokens '''

        que = Que(iterator)

        line = 1
        while que.peek() is not None:
            c = que.next()
            if c == '#':
                count = 1
                while que.peek() is not None and que.peek() == '#':
                    que.next()
                    count += 1

                star = que.peek() == '*'
                if star:
                    que.next()

                consume_single_spaces(que)
                yield ("section", line, count, star)
            elif c == '$':
                if que.peek() == '$':
                    que.next()
                    yield ("displaymath", line)
                else:
                    yield ("math", line)
            elif c == '*':
                yield ("*", line)
            elif c == '\n':
                yield ("newline", line)
                line += 1
            elif c == '\\':
                s = ""
                if que.peek() in token_first:
                    # Consume single character, likely escaping ( or )
                    s = que.next()
                else:
                    # Consume next word
                    while (
                            not que.peek().isspace() and
                            que.peek() not in token_first and
                            que.peek() is not None):
                        s += que.next()

                yield ("escaped", line, s)
            elif c == '(':
                yield ("lparen", line)
            elif c == ')':
                yield ("rparen", line)
            elif c == '[':
                yield ("lbracket", line)
            elif c == ']':
                yield ("rbracket", line)
            else:
                s = c
                while que.peek() not in token_first and que.peek() is not None:
                    s += que.next()

                acc = []

                # Split into word and non-word parts
                for fragment in re.findall(r"\w+|[^\w]", s, re.UNICODE):
                    if fragment in keywords:
                        if len(acc) > 0:
                            yield ("text", line, ''.join(acc))

                        yield ("keyword", line, fragment)
                        acc = []
                    else:
                        acc.append(fragment)

                if len(acc) > 0:
                    yield ("text", line, ''.join(acc))

    def generate(stream, mathmode, in_document):
        paren_counter = 0
        output = []
        que = Que(stream)

        while True:
            token = que.next()

            if token is None:
                break

            if token[0] == "text":
                output.append(token[2])
            elif token[0] == "newline":
                output.append("\n")
            elif token[0] == "*":
                if mathmode:
                    output.append("\\cdot ")
                else:
                    output.append("*")
            elif token[0] == "escaped":
                if token[2] != '(' and token[2] != ')':
                    output.append("\\")

                output.append(token[2])

                if token[2] == "begin{document}":
                    in_document = True

                if token[2] == "end{document}":
                    in_document = False

            elif token[0] == "math":
                if mathmode:
                    print("Expected $$ found $ on line " + str(token[1]))

                output.append("$")
                inner = generate(takewhile(lambda tok: tok[0] != "math", stream), True, in_document)
                output.append(inner)
                output.append("$")
            elif token[0] == "displaymath":
                if mathmode:
                    print("Expected $ found $$ on line " + str(token[1]))

                output.append("$$")
                substream = takewhile(lambda tok: tok[0] != "displaymath", stream)
                inner = generate(substream, True, in_document)
                output.append(inner)
                output.append("$$")
            elif token[0] == "section":
                # section, subsection, subsubsection, etc.
                sectioncommand = '\\' + ''.join(["sub" * (token[2] - 1)]) + "section"
                if token[3]:
                    sectioncommand += '*'

                output.append(sectioncommand + "{")
                substream = takewhile(lambda tok: tok[0] != "newline", stream)
                output.append(generate(substream, mathmode, in_document))
                output.append("}\n")
            elif token[0] == "keyword":
                if mathmode:
                    output.append("\\" + token[2])
                else:
                    output.append(token[2])
            elif token[0] == "lbracket":
                if mathmode or not in_document:
                    output.append("[")
                else:
                    substream = takewhile(lambda tok: tok[0] != "rbracket", stream)
                    inner = generate(substream, mathmode, in_document)
                    if True or len(inner) > 30:
                        # Who uses cite keys this long?
                        # Assume something else was intended
                        output.append("[")
                        output.append(inner)
                        output.append("]")
                    else:
                        output.append("\\cite{")
                        output.append(inner)
                        output.append("}")
            elif token[0] == "rbracket":
                output.append("]")
            elif token[0] == "lparen":
                prev = que.prev()
                prev_is_left = prev is not None and prev[0] == "escaped" and prev[2] == "left"
                if mathmode and in_document and not prev_is_left:
                    paren_counter += 1
                    output.append("\\left(")
                else:
                    output.append("(")
            elif token[0] == "rparen":
                prev = que.prev()
                prev_is_right = prev is not None and prev[0] == "escaped" and prev[2] == "right"
                if mathmode and in_document and not prev_is_right:
                    paren_counter -= 1
                    output.append("\\right)")
                else:
                    output.append(")")
            else:
                sys.stderr.write("Unhandled token '" + str(token))
                sys.stderr.flush()
                exit(1)

        if paren_counter != 0:
            sys.stderr.write("Parentheses are not matched on line " + str(que.prev()[1]) +
                             ". Delta " + str(paren_counter) + "\n")

            # Write last 80 characters of buffer
            sys.stderr.write(''.join(output)[-80:])
            sys.stderr.flush()
            exit(1)

        return ''.join(output)

    return generate(tokenize(iter(input)), False, False)


args = [arg for arg in sys.argv[1:] if arg.startswith("-")]
path = sys.argv[-1]

input_text = open(path, "rt", encoding="utf-8").read()

output = process(input_text)

# Remove '.tex' extension
path = path[:-4]

tmp_path = path + ".tmp"
open(tmp_path + ".tex", "wt", encoding="utf-8").write(output)


def move_if_exists(from_path, to_path):
    if os.path.isfile(from_path):
        shutil.move(from_path, to_path)


def mvtex(from_path, to_path):
    move_if_exists(from_path + ".synctex.gz", to_path + ".synctex.gz")
    move_if_exists(from_path + ".log", to_path + ".log")
    move_if_exists(from_path + ".aux", to_path + ".aux")
    move_if_exists(from_path + ".pdf", to_path + ".pdf")


mvtex(path, tmp_path)

call(["pdflatex"] + args + [tmp_path + ".tex"])

mvtex(tmp_path, path)
os.remove(tmp_path + ".tex")
