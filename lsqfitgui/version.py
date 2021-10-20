"""Version infos."""
import os

_VERSION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "_version.txt"))


with open(_VERSION_FILE) as inp:
    __version__ = inp.read()
