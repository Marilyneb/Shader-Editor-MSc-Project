from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget, QMessageBox, QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor, QTextCursor, QPainter
from PySide6.QtCore import Qt, QRegularExpression, QRect, QSize


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


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
            "gl_FragCoord", "gl_FragColor", "gl_Position", "vec2", "vec3", "vec4", "mat2", "mat3", "mat4",
            "discard", "return", "layout", "invariant", "noperspective", "flat", "smooth", "centroid",
            "isampler2D", "isampler3D", "isamplerCube", "usampler2D", "usampler3D", "usamplerCube"
        ]

        self.keyword_patterns = [QRegularExpression(f"\\b{keyword}\\b") for keyword in keywords]

        self.preprocessor_format = QTextCharFormat()
        self.preprocessor_format.setForeground(QColor(Qt.darkCyan))
        self.preprocessor_patterns = [QRegularExpression("#[a-zA-Z_]+")]

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(Qt.darkGreen))
        self.comment_patterns = [QRegularExpression("//[^\n]*"), QRegularExpression("/\\*.*\\*/")]

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(Qt.darkMagenta))
        self.function_patterns = [QRegularExpression("\\b[a-zA-Z_][a-zA-Z0-9_]*(?=\\()")]

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(Qt.darkRed))
        self.number_pattern = QRegularExpression("\\b[0-9]+(\\.[0-9]+)?\\b")

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(Qt.darkYellow))
        self.string_patterns = [QRegularExpression("\".*\""), QRegularExpression("\'.*\'")]

    def highlightBlock(self, text):
        for pattern in self.keyword_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.keyword_format)

        for pattern in self.preprocessor_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.preprocessor_format)

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

        match_iterator = self.number_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.number_format)

        for pattern in self.string_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), self.string_format)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)

        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.highlighter = GLSLSyntaxHighlighter(self.document())

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.match_brackets)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.yellow).lighter(160)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextCharFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def get_code(self):
        return self.toPlainText()

    def set_code(self, code):
        self.setPlainText(code)

    def highlight_errors(self, error_message):
        error_lines = self.parse_errors(error_message)
        extraSelections = []
        for line_num, msg in error_lines:
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(Qt.red).lighter(160))
            line_cursor = QTextCursor(self.document().findBlockByLineNumber(line_num - 1))
            selection.cursor = line_cursor
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
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

    def match_brackets(self):
        cursor = self.textCursor()
        text = self.toPlainText()
        pos = cursor.position()

        if pos > 0:
            char = text[pos - 1]
            match = None

            if char in "([{":
                match = self.find_matching_bracket(text, pos - 1, char)
            elif char in ")]}":
                match = self.find_matching_bracket(text, pos - 1, char, forward=False)

            extraSelections = []

            if match is not None:
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(QColor(Qt.cyan).lighter(130))
                selection.cursor = QTextCursor(self.document())
                selection.cursor.setPosition(match)
                selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
                extraSelections.append(selection)

            self.setExtraSelections(extraSelections)

    def find_matching_bracket(self, text, pos, char, forward=True):
        brackets = {"(": ")", "[": "]", "{": "}", ")": "(", "]": "[", "}": "{"}
        stack = 1
        direction = 1 if forward else -1

        for i in range(pos + direction, len(text) if forward else -1, direction):
            if text[i] == char:
                stack += 1
            elif text[i] == brackets[char]:
                stack -= 1

            if stack == 0:
                return i

        return None


class CodeEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.editor = CodeEditor()
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def get_code(self):
        return self.editor.get_code()

    def set_code(self, code):
        self.editor.set_code(code)

    def highlight_errors(self, error_message):
        self.editor.highlight_errors(error_message)
