from textwrap import dedent
import asyncio
import os

from carbon.carbon import get_response
from carbon.utility import createURLString, validateBody

# https://github.com/cyberboysumanjay/Carbon-API/issues/9
NEW_LINE = "%250A"

loop = asyncio.get_event_loop()


def _create_carbon_compatible_newlines(code):
    return code.replace("\n", NEW_LINE)


def create_carbon_image(payload: dict[str, str], outfile: str) -> str:
    payload["code"] = _create_carbon_compatible_newlines(payload["code"])
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
    payload = {
        "code": dedent(quote).strip(),
        "backgroundColor": "C4F2FD",
        "theme": "Material",
        "language": "Plain Text",
    }
    # ret = create_carbon_image(payload, "out.png")
    # print(ret)

    code = """
    >>> from operator import itemgetter

    >>> days = ['mon', 'tue', 'wed', 'thurs', 'fri', 'sat', 'sun']
    >>> f = itemgetter(3, 6)
    >>> f(days)
    ('thurs', 'sun')
    """
    payload = {
        "code": dedent(code).strip(),
        "theme": "Sethi",
        "language": "Python",
    }
    ret = create_carbon_image(payload, "out.png")
    print(ret)
