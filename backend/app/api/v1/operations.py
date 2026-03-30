from fastapi import APIRouter

from app.engine.registry import OperationRegistry
from app.schemas.operation import OperationListResponse

import app.engine.operations  # noqa: F401

router = APIRouter(prefix="/operations", tags=["operations"])


@router.get("", response_model=OperationListResponse)
async def list_operations():
    ops = OperationRegistry.list_operations()
    return OperationListResponse(operations=ops)
