from datetime import datetime
import importlib
from types import SimpleNamespace
from uuid import uuid4
import sys
from pathlib import Path
from sqlalchemy.exc import IntegrityError

import jwt

APP_ROOT = Path(__file__).resolve().parents[1]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

