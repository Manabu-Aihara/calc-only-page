import pytest

import sys

# sys.path.append(os.path.abspath(".."))
import pathlib
from os.path import join, dirname

from dotenv import load_dotenv


packagedir = pathlib.Path(__file__).resolve().parent.parent.parent
print(packagedir)
sys.path.append(str(packagedir))

dotenv_path = join(str(packagedir), ".env")
load_dotenv(dotenv_path)
