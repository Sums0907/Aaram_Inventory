import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.category import CategoryModel
from src.foundation.enums import ItemType
from src.domains.masters.services.category_ownership import CategoryOwnershipResolver

@pytest.mark.asyncio
async def test_category_domain_001_item_type_is_fg_but_ancestor_is_rm(db_session: AsyncSession):
    """
    CATEGORY-DOMAIN-001
    Given: category.item_type = FINISHED_GOODS, but ancestor root = RM
    Expected: Domain = OPERATIONAL
    """
    # Create RM root
    rm_root = CategoryModel(category_code="RM", category_name="Raw Materials", item_type=ItemType.FINISHED_GOODS)
    db_session.add(rm_root)
    await db_session.flush()

    # Create child with incorrect item_type
    rm_child = CategoryModel(category_code="RM-FABRIC", category_name="Fabric", parent_id=rm_root.id, item_type=ItemType.FINISHED_GOODS)
    db_session.add(rm_child)
    await db_session.flush()

    resolver = CategoryOwnershipResolver(db_session)
    result = await resolver.resolve("RM-FABRIC")
    
    assert result["domain"] == "OPERATIONAL"
    assert result["root_code"] == "RM"
    assert result["category_path"] == "RM/RM-FABRIC"

@pytest.mark.asyncio
async def test_category_domain_002_item_type_is_rm_but_ancestor_is_fg(db_session: AsyncSession):
    """
    CATEGORY-DOMAIN-002
    Given: category.item_type = RAW_MATERIAL, but ancestor root = FG
    Expected: Domain = FINISHED_GOODS
    """
    # Create FG root
    fg_root = CategoryModel(category_code="FG", category_name="Finished Goods", item_type=ItemType.RAW_MATERIAL)
    db_session.add(fg_root)
    await db_session.flush()

    # Create child with incorrect item_type
    fg_child = CategoryModel(category_code="FG-BED", category_name="Bedsheet", parent_id=fg_root.id, item_type=ItemType.RAW_MATERIAL)
    db_session.add(fg_child)
    await db_session.flush()

    resolver = CategoryOwnershipResolver(db_session)
    result = await resolver.resolve("FG-BED")
    
    assert result["domain"] == "FINISHED_GOODS"
    assert result["root_code"] == "FG"
    assert result["category_path"] == "FG/FG-BED"

@pytest.mark.asyncio
async def test_category_domain_003_missing_root_ancestor(db_session: AsyncSession):
    """
    CATEGORY-DOMAIN-003
    Missing root ancestor
    Expected: Validation failure
    """
    # Create invalid root
    invalid_root = CategoryModel(category_code="INVALID", category_name="Invalid Root")
    db_session.add(invalid_root)
    await db_session.flush()

    invalid_child = CategoryModel(category_code="INVALID-CHILD", category_name="Invalid Child", parent_id=invalid_root.id)
    db_session.add(invalid_child)
    await db_session.flush()

    resolver = CategoryOwnershipResolver(db_session)
    
    with pytest.raises(ValueError, match="Invalid root ancestor 'INVALID'"):
        await resolver.resolve("INVALID-CHILD")
