import asyncio
from src.foundation.authentication.dependencies import get_current_user, require_permission, CurrentIdentityContext
from src.foundation.exceptions.base import ForbiddenException
from typing import List

# Mock payload as seen in the logs
token = "ey..." # not needed, we'll just mock get_current_user directly

user = CurrentIdentityContext(
    user_id="55",
    name="Sumati Dhingra",
    applications=["AARAM_BOOKS", "AARAM_INVENTORY", "AARAM_PACKING"],
    roles=["AARAM_PACKING_ADMIN", "AARAM_INVENTORY_ADMIN"],
    permissions=["INVENTORY_JOBWORK_VIEW", "INVENTORY_ACTIVITY_VIEW"]
)

perm_checker = require_permission("INVENTORY_JOBWORK_VIEW")
try:
    perm_checker(user=user)
    print("Permission check passed!")
except ForbiddenException as e:
    print(f"Failed: {e}")

