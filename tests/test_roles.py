import pytest
from fastapi import Request, HTTPException, status
from unittest.mock import MagicMock

from src.conf import messages
from src.entity.models import Role, User
from src.services.roles import RoleAccess


@pytest.mark.asyncio
async def test_role_access_allowed():
    allowed_roles = [Role.admin, Role.moderator]
    admin_user = User(role=Role.admin)  # Create a user with admin role
    request = MagicMock(spec=Request)

    role_access = RoleAccess(allowed_roles)

    # Call the RoleAccess instance as a coroutine
    await role_access(request, user=admin_user)


@pytest.mark.asyncio
async def test_role_access_forbidden():
    allowed_roles = [Role.admin, Role.moderator]
    user = User(role=Role.user)  # Create a user with user role
    request = MagicMock(spec=Request)

    role_access = RoleAccess(allowed_roles)

    # Call the RoleAccess instance as a coroutine and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await role_access(request, user=user)

    # Assert that the exception has the correct status code and detail message
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == messages.ACCESS_FORBIDDEN
