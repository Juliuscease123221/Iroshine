"""
iroshine.code_styles — build a code colour scheme from a palette, for CodePanel(style=...).

    CodePanel(style=code_style(text="#e9e6f2", keyword="#e8a9c4", string="#f0a870", number="#6fb3a2",
                               comment="#7c83b8", name="#e9e6f2"), ...)
"""
from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text, Token


def code_style(text="#e8e4dc", keyword="#e8a9c4", string="#f0a870", number="#6fb3a2", comment="#7c83b8",
               name=None, operator=None, background="#000000"):
    class _S(Style):
        background_color = background
        styles = {
            Token: text, Text: text, Name: name or text, Name.Builtin: name or text,
            Name.Function: name or text,
            Keyword: keyword, Keyword.Constant: keyword, Operator.Word: keyword,
            Operator: operator or text, Punctuation: text,
            String: string, Number: number, Comment: "italic " + comment,
        }
    return _S
