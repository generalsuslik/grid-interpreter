from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor
from lark import Lark


class Lexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.procedures = []
        self.variables = []
        self.create_parser()
        self.create_styles()

    def create_styles(self):
        deeppink = QColor(249, 38, 114)
        khaki = QColor(230, 219, 116)
        mediumpurple = QColor(174, 129, 255)
        mediumturquoise = QColor(81, 217, 205)
        yellowgreen = QColor(166, 226, 46)
        lightcyan = QColor(213, 248, 232)
        darkslategrey = QColor(34, 34, 34)
        blue = QColor(60, 137, 240)
        orange = QColor(255, 127, 80)
        grey = QColor(230, 230, 230)

        styles = {
            0: mediumturquoise,
            1: mediumpurple,
            2: yellowgreen,
            3: deeppink,
            4: khaki,
            5: lightcyan,
            6: blue,
            7: orange,
            8: grey,
        }

        for style, color in styles.items():
            self.setColor(color, style)
            self.setPaper(darkslategrey, style)
            self.setFont(self.parent().font(), style)

        self.token_styles = {
            "COLON": 5,
            "COMMA": 5,
            "LBRACE": 5,
            "LSQB": 5,
            "RBRACE": 5,
            "RSQB": 5,
            "NULL": 0,
            "STRING": 4,
            "NUMBER": 1,
            "COMMAND": 6,
            "PROCEDURE": 6,
            "DEF": 7,
            "VARIABLE": 8,
        }

    def create_parser(self):
        commands = [
            "\"RIGHT\"",
            "\"LEFT\"",
            "\"UP\"",
            "\"DOWN\"",
            "\"IFBLOCK\"",
            "\"ENDIF\"",
            "\"REPEAT\"",
            "\"ENDREPEAT\"",
            "\"SET\"",
        ]
        grammar = fr"""
            anons: ":" "{{" "}}" "," "[" "]" "="
            COMMAND: {" | ".join(commands)}
            {'PROCEDURE: "' + '" | "'.join(self.procedures) + '"'
                if self.procedures else ""}
            {'VARIABLE: "' + '" | "'.join(self.variables) + '"'
                if self.variables else ""}
            FUNC: /PROCEDURE \w+[ \n]/
            SET: /SET \w+[ \n]/
            DEF: "ENDPROC" | "CALL"
            %import common.ESCAPED_STRING -> STRING
            %import common.SIGNED_NUMBER  -> NUMBER
            %import common.WS
            %ignore WS
        """
        self.lark = Lark(grammar, parser=None, lexer="basic")

    def defaultPaper(self, style):
        return QColor("#222222")

    def language(self):
        return "?"

    def description(self, style):
        return {v: k for k, v in self.token_styles.items()}.get(style, "")

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.parent().text()[start:end]
        last_pos = 0
        try:
            for token in self.lark.lex(text):
                ws_len = token.start_pos - last_pos
                if ws_len:
                    self.setStyling(ws_len, 0)    # whitespace
                token_len = len(bytearray(token, "utf-8"))
                tt = token.type

                if tt == "FUNC":
                    def_style = self.token_styles.get("DEF", 0)
                    command_style = self.token_styles.get("COMMAND", 0)
                    self.setStyling(9, def_style)
                    self.setStyling(token_len - 9, command_style)
                    procedure_name = token[10:-1]
                    if procedure_name not in self.procedures:
                        self.procedures.append(procedure_name)
                        self.create_parser()
                elif tt == "SET":
                    def_style = self.token_styles.get("DEF", 0)
                    variable_style = self.token_styles.get("VARIABLE", 0)
                    self.setStyling(3, def_style)
                    self.setStyling(token_len - 3, variable_style)
                    variable_name = token[4:-1]
                    if variable_name not in self.variables:
                        self.variables.append(variable_name)
                        self.create_parser()
                else:
                    self.setStyling(
                        token_len, self.token_styles.get(token.type, 0))

                last_pos = token.start_pos + token_len
        except Exception:
            pass
