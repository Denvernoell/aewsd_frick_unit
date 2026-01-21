from fasthtml.common import *
from loguru import logger


def _not_found(req, exc):
    return Titled("Oh no!", Div("We could not find that page :("))


# import sys

# sys.path.append("..")
# from shared.paths import paths

from monsterui.all import *
hdrs = Theme.blue.headers(
    mode='light',
)


app = FastHTML(
    # before=bware,
    # These are the same as Starlette exception_handlers, except they also support `FT` results
    exception_handlers={404: _not_found},
    routes=[ ],
    hdrs=hdrs,
)



rt = app.route
