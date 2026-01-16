from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.restaurant import Restaurant, Branch
from app.models.user import User
from app.schemas.branch import Branch as BranchSchema, BranchCreate, BranchUpdate

router = APIRouter()

@router.get("/", response_model=List[BranchSchema])
async def read_branches(
    db: AsyncSession = Depends(get_db),
    restaurant_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve branches. Optionally filter by restaurant_id.
    """
    query = select(Branch)
    
    if restaurant_id:
        query = query.where(Branch.restaurant_id == restaurant_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{branch_id}", response_model=BranchSchema)
async def read_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get branch by ID.
    """
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalars().first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.post("/", response_model=BranchSchema)
async def create_branch(
    *,
    db: AsyncSession = Depends(get_db),
    branch_in: BranchCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new branch for a restaurant.
    """
    # Verify restaurant exists
    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == branch_in.restaurant_id)
    )
    if not rest_result.scalars().first():
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    branch = Branch(**branch_in.model_dump())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch

@router.put("/{branch_id}", response_model=BranchSchema)
async def update_branch(
    *,
    db: AsyncSession = Depends(get_db),
    branch_id: int,
    branch_in: BranchUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a branch.
    """
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalars().first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    update_data = branch_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch

@router.delete("/{branch_id}")
async def delete_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a branch.
    """
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalars().first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    await db.delete(branch)
    await db.commit()
    return {"message": "Branch deleted successfully"}
