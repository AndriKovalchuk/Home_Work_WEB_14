from datetime import datetime
from io import BytesIO
from unittest.mock import AsyncMock, patch

from src.schemas.user import UserResponse
from src.services.auth import auth_service


def test_get_me(client, get_token, monkeypatch):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        # Passing RateLimiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get("api/users/me", headers=headers)
        assert response.status_code == 200, response.text


def test_upload_avatar(client, get_token, monkeypatch):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        with patch("cloudinary.uploader.upload") as upload_mock:
            upload_mock.return_value = {
                "public_id": "test_image",
                "version": "1234567890",
                "url": "https://example.com/test_image.jpg",
            }

            with patch("cloudinary.CloudinaryImage.build_url") as build_url_mock:
                build_url_mock.return_value = "https://example.com/test_image.jpg"

                mock_update_avatar_url = AsyncMock()
                mock_update_avatar_url.return_value = UserResponse(
                    username="test_username",
                    role="admin",
                    email="test@example.com",
                    avatar="https://example.com/test_image.jpg"
                )
                monkeypatch.setattr(
                    "src.repository.users.update_avatar_url",
                    mock_update_avatar_url
                )

                file_content = b"dummy_image_content"
                file = BytesIO(file_content)

                response = client.patch("api/users/avatar", headers=headers, files={"file": file})

                assert response.status_code == 200
                data = response.json()
                assert data["avatar"] == "https://example.com/test_image.jpg"
