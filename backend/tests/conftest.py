import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure backend and root project directories are in Python path
backend_path = Path(__file__).resolve().parent.parent
root_path = backend_path.parent

if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from app.main import app

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
