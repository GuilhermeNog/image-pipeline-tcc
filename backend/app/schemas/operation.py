from pydantic import BaseModel


class OperationSchema(BaseModel):
    name: str
    params: dict


class OperationListResponse(BaseModel):
    operations: list[OperationSchema]
