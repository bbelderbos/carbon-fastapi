from textwrap import dedent
import asyncio

from carbon.carbon import get_response
from carbon.utility import createURLString, validateBody

# https://github.com/cyberboysumanjay/Carbon-API/issues/9
NEW_LINE = "%250A"
DEFAULT_THEME = "Sethi"
DEFAULT_LANGUAGE = "Python"

loop = asyncio.get_event_loop()


def _create_payload(code, kwargs):
    payload = {
        "code": code.replace("\n", NEW_LINE),
        "theme": kwargs.pop("theme", DEFAULT_THEME),
        "language": kwargs.pop("language", DEFAULT_LANGUAGE),
    }
    payload.update(kwargs)
    return payload


def create_carbon_image(code: str, outfile: str, **kwargs: dict[str, str]) -> str:
    payload = _create_payload(code, kwargs)
    validatedBody = validateBody(payload)
    carbonURL = createURLString(validatedBody)
    result_file = loop.run_until_complete(
         get_response(carbonURL, outfile))
    return result_file


if __name__ == "__main__":
    quote = """
        "Don't worry about getting it right. Just get it started."
        - Marie Forleo
    """
    code = dedent(quote).strip()
    payload = {
        "backgroundColor": "C4F2FD",
        "theme": "Material",
        "language": "Plain Text",
    }
    # ret = create_carbon_image(code, "out.png", **payload)
    # print(ret)

    code = """
    >>> from operator import itemgetter

    >>> days = ['mon', 'tue', 'wed', 'thurs', 'fri', 'sat', 'sun']
    >>> f = itemgetter(3, 6)
    >>> f(days)
    ('thurs', 'sun')
    """
    code = dedent(code).strip()
    ret = create_carbon_image(code, "out.png")
    print(ret)
