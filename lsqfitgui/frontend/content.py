""""""
from dash import html


def get_content(fit):
    content = html.Div(
        children=[
            html.H1(children="Hello World!"),
            html.Pre(children=fit.format(maxline=True)),
        ]
    )
    return content
