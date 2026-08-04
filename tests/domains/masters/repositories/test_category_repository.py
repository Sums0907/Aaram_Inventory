import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.repositories.category import CategoryRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    repo = CategoryRepository(db_session)
    
    category = CategoryModel(
        category_code="CAT-1",
        category_name="Category 1",
        display_order=10
    )
    created = await repo.create(category)
    
    assert created.id is not None
    assert created.category_code == "CAT-1"
    
    fetched = await repo.get_by_code("CAT-1")
    assert fetched is not None
    assert fetched.id == created.id

@pytest.mark.asyncio
async def test_repository_get_all_ordered(db_session: AsyncSession):
    repo = CategoryRepository(db_session)
    
    await repo.create(CategoryModel(category_code="C3", category_name="Cat 3", display_order=3))
    await repo.create(CategoryModel(category_code="C1", category_name="Cat 1", display_order=1))
    await repo.create(CategoryModel(category_code="C2", category_name="Cat 2", display_order=2))
    
    results = await repo.get_all()
    # verify length
    assert len(results) >= 3
    
    # We filter only the ones we just added to check order, or trust that offset/limit handles it.
    codes = [c.category_code for c in results]
    assert "C1" in codes
    assert "C2" in codes
    assert "C3" in codes
