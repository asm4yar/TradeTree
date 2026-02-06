from fastapi import APIRouter, Depends
from app.api.catalog.schemas import CategoryChildrenCountOut
from app.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter(prefix="/categories", tags=["Catalog / Categories"])

SQL_CHILDREN_COUNT = text(
    """
select
	c.id,
	c.name,
	COUNT(child.id) as children_count
from
	categories c
join categories parent on
	parent.id = c.parent_id
left join categories child on
	child.parent_id = c.id
where
	parent.parent_id is null
group by
	c.id,
	c.name
order by
	c.name;
"""
)


@router.get("/children-count", response_model=list[CategoryChildrenCountOut])
async def get_children_count_first_level(db: Session = Depends(get_db)):
    res = db.execute(SQL_CHILDREN_COUNT)
    rows = res.mappings().all()
    return rows
