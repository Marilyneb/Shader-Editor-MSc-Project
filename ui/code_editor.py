# code_editor.py
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QTextCursor
from PySide6.QtCore import Qt, QRegularExpression

class GLSLSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(Qt.blue))
        self.keyword_format.setFontWeight(QFont.Bold)

        keywords = [
            "attribute", "const", "uniform", "varying", "break", "continue", "do", "for", "while",
            "if", "else", "in", "out", "inout", "float", "int", "void", "bool", "true", "false",
            "lowp", "mediump", "highp", "precision", "sampler2D", "samplerCube", "struct",
            "gl_FragCoord", "gl_FragColor", "gl_Position", "vec2", "vec3", "vec4", "mat2", "mat3", "mat4"
        ]

        self.keyword_patterns = [QRegularExpression(f"\\b{keyword}\\b") for keyword in keywords]

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(Qt.darkGreen))
        self.comment_patterns = [QRegularExpression("//[^\n]*"), QRegularExpression("/\\*.*\\*/")]

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(Qt.darkMagenta))
        self.function_patterns = [QRegularExpression("\\b[a-zA-Z_][a-zA-Z0-9_]*(?=\\()")]

    def highlightBlock(self, text):
        for pattern in self.keyword_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.keyword_format)

        for pattern in self.comment_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.comment_format)

        for pattern in self.function_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.function_format)

class CodeEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(QTextEdit.NoWrap)
        self.highlighter = GLSLSyntaxHighlighter(self.editor.document())

        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def get_code(self):
        return self.editor.toPlainText()

    def set_code(self, code):
        self.editor.setPlainText(code)

    def highlight_errors(self, error_message):
        error_lines = self.parse_errors(error_message)
        extraSelections = []
        for line_num, msg in error_lines:
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(Qt.red).lighter(160))
            line_cursor = QTextCursor(self.editor.document().findBlockByLineNumber(line_num - 1))
            selection.cursor = line_cursor
            extraSelections.append(selection)
        self.editor.setExtraSelections(extraSelections)
        QMessageBox.warning(self, "Shader Compilation Errors", error_message)

    def parse_errors(self, error_message):
        error_lines = []
        for line in error_message.splitlines():
            if "ERROR:" in line:
                parts = line.split(":")
                if len(parts) >= 3 and parts[1].isdigit():
                    line_num = int(parts[1])
                    error_lines.append((line_num, line))
        return error_lines
