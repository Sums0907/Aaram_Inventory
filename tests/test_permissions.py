import unittest
from src.foundation.authentication.dependencies import require_permission, CurrentIdentityContext
from src.foundation.exceptions.base import ForbiddenException

class TestPermissions(unittest.TestCase):
    def test_require_permission_success(self):
        user = CurrentIdentityContext(
            user_id="123",
            name="Test",
            applications=["AARAM_BOOKS"],
            roles=["OWNER"],
            permissions=["INVENTORY_RECEIPT_CREATE"]
        )
        
        dep = require_permission("INVENTORY_RECEIPT_CREATE")
        result = dep(user=user)
        self.assertEqual(result.user_id, "123")

    def test_require_permission_forbidden(self):
        user = CurrentIdentityContext(
            user_id="123",
            name="Test",
            applications=["AARAM_BOOKS"],
            roles=["AARAM_BOOKS_INVENTORY_MANAGER"],
            permissions=["INVENTORY_RECEIPT_CREATE"]
        )
        
        dep = require_permission("INVENTORY_TRANSFORMATION_CREATE")
        with self.assertRaises(ForbiddenException) as context:
            dep(user=user)
        
        self.assertTrue("Missing required permission: INVENTORY_TRANSFORMATION_CREATE" in str(context.exception.message))

if __name__ == '__main__':
    unittest.main()
