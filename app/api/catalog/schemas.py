from pydantic import BaseModel, Field


class AddItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class AddItemResponse(BaseModel):
    order_id: int
    product_id: int
    new_qty: int
    remaining_stock: int


class CategoryChildrenCountOut(BaseModel):
    id: int
    name: str
    children_count: int


class clientStatistics(BaseModel):
    name: str
    total_amount: int
