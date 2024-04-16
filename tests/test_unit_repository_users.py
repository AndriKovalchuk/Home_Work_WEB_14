import unittest
from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repository.users import (confirmed_email, create_user,
                                  get_user_by_email, store_reset_token,
                                  update_avatar_url, update_password,
                                  update_token, verify_reset_token)
from src.schemas.user import UserModel, UserResponse
from src.services.auth import Auth


class TestAsyncUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        user = UserModel(id=1,
                         username="username",
                         email='user@example.com',
                         password="password")

        mocked_user = Mock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(user.email, self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(username="username",
                         email='user@example.com',
                         password="password")

        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)

    async def test_update_token(self):
        refresh_token = None
        with patch.object(self.session, 'commit') as mock_db_commit:
            result = await update_token(self.user, refresh_token, self.session)
            mock_db_commit.assert_called_once()
            self.assertEqual(result, refresh_token)

    async def test_confirmed_email(self):
        user = User(username="username",
                    email='user@example.com',
                    password="password",
                    confirmed=False)

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            mock_session_commit = AsyncMock()
            self.session.commit = mock_session_commit

            result = await confirmed_email(user.email, self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)
            mock_session_commit.assert_called_once()
            self.assertIsNone(result)

    async def test_update_avatar_url(self):
        user = User(username="username",
                    email='user@example.com',
                    password="password",
                    avatar="avatar_url")

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            mock_session_commit = AsyncMock()
            self.session.commit = mock_session_commit

            result = await update_avatar_url(user.email, "another_avatar_url", self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)
            mock_session_commit.assert_called_once()
            self.assertEqual(result.avatar, "another_avatar_url")

    async def test_store_reset_token(self):
        user = User(username="username",
                    email='user@example.com',
                    password="secret_password",
                    avatar="avatar_url",
                    reset_token=None)

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            mock_session_commit = AsyncMock()
            self.session.commit = mock_session_commit

            result = await store_reset_token(user.email, "reset_token", self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)
            mock_session_commit.assert_called_once()

            self.assertEqual(result, user)

    async def test_verify_reset_token(self):
        user = User(username="username",
                    email='user@example.com',
                    password="password",
                    avatar="avatar_url",
                    reset_token="reset_token")

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            result = await verify_reset_token(user.email, "reset_token", self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)

            self.assertTrue(result)

    async def test_update_password(self):
        user = User(username="username",
                    email='user@example.com',
                    password="password",
                    avatar="avatar_url",
                    reset_token="reset_token")

        with patch('src.repository.users.get_user_by_email') as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user

            mock_session_commit = AsyncMock()
            self.session.commit = mock_session_commit

            new_password = "new_pass"
            hashed_new_password = Auth.pwd_context.hash(new_password)

            result = await update_password(user.email, hashed_new_password, self.session)

            mock_get_user_by_email.assert_called_once_with(user.email, self.session)
            mock_session_commit.assert_called_once()

            self.assertTrue(Auth.pwd_context.verify(hashed_new_password, result.password))


if __name__ == '__main__':
    unittest.main()
