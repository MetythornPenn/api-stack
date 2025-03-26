from typing import AsyncGenerator, Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# Re-export get_db for convenience
get_db = get_db