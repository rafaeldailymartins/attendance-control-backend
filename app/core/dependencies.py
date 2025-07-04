from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import get_session

SessionDepends = Annotated[Session, Depends(get_session)]
