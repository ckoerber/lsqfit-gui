""""""
from dash import html


def get_content(fit, name: str = "Lsqfit GUI"):
    content = html.Div(
        children=[html.H1(children=name), html.Pre(children=fit.format(maxline=True)),]
    )
    return content
