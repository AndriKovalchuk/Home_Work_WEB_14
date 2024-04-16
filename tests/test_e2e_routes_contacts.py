from datetime import datetime
from io import BytesIO
from unittest.mock import AsyncMock, patch

from fastapi import status, HTTPException
from starlette.testclient import TestClient

from main import app
from src.conf import messages
from src.routes.contacts import MAX_FILE_SIZE
from src.services.auth import auth_service


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d')
    raise TypeError("Type not serializable")


"""
Отримати список всіх контактів.
"""


def test_get_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        # Passing RateLimiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get("api/contacts", headers=headers)
        print(f"RESPONSE: {response.json()}")
        assert response.status_code == 200, response.text
        data = response.json()
        print(f"DATA: {data}")
        assert isinstance(data, list)
        assert len(data) == 0


"""
Отримати список всіх контактів. all
"""


def test_get_all_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, "cache") as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        # Passing RateLimiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get("api/contacts/all", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        print(data)
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["first_name"] == "James config"


"""
Створити новий контакт.
"""


def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, "cache") as redis_mock:  # Цей рядок мокує атрибут cache об'єкта auth_service.
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        birth_date = datetime(1990, 4, 20)

        # Passing RateLimiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        # Надсилає POST-запит до точки доступу для створення нового контакту. Запит включає заголовки та JSON-пакет, що представляє дані контакту.
        response = client.post("api/contacts", headers=headers, json={
            "first_name": "James II",
            "last_name": "Bond II",
            "email": "jamesII@gmail.com",
            "contact_number": "222-222-2222",
            "birth_date": json_serial(birth_date),
            "additional_information": None,
        })
        assert response.status_code == 201, response.text  # Перевіряє, чи статус відповіді - 201, що вказує на успішне створення контакту.
        data = response.json()  # Розбирає JSON-вміст відповіді в словник Python з ім'ям data
        assert "id" in data  # Перевіряє, що відповідь містить ключ "id".
        assert data[
                   "first_name"] == "James II"  # Перевірка окремих полів створеного контакту, щоб переконатися, що вони відповідають наданим даним.
        assert data["last_name"] == "Bond II"
        assert data["email"] == "jamesII@gmail.com"
        assert data["contact_number"] == "222-222-2222"
        assert data["birth_date"] == json_serial(birth_date)


"""
Отримати один контакт за ідентифікатором.
"""


def test_get_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, "cache") as redis_mock:  # Цей рядок мокує атрибут cache об'єкта auth_service.
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        # Passing RateLimiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        # Надсилає POST-запит до точки доступу для пошуку контакту за id=1. Запит включає заголовки та JSON-пакет, що представляє дані контакту.
        response = client.get("api/contacts/2", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        print(data)
        assert data["id"] == 2
        assert data["first_name"] == "James II"


"""
Отримати один контакт за ідентифікатором, який не існує.
"""


def test_get_contact_not_found(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:  # Цей рядок мокує атрибут cache об'єкта auth_service.
        redis_mock.get.return_value = None  # Це налаштовує поведінку мокованого кешу Redis, забезпечуючи, що він повертатиме None.
        token = get_token  # Отримує токен за допомогою фікстури get_token із conftest.py
        headers = {"Authorization": f"Bearer {token}"}  # Створює заголовки з отриманим токеном для автентифікації.

        # Mock Rate Limiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get("/api/contacts/9", headers=headers)

        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NOT_FOUND


"""
Оновити існуючий контакт.
"""


def test_update_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token  # Отримує токен за допомогою фікстури get_token із conftest.py
        headers = {"Authorization": f"Bearer {token}"}  # Створює заголовки з отриманим токеном для автентифікації.
        new_birth_date = datetime(2003, 4, 20)

        # Mock Rate Limiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.put("/api/contacts/2",
                              json={"first_name": "James_updated",
                                    "last_name": "Bond",
                                    "email": "james_updated@gmail.com",
                                    "contact_number": "333-333-3333",
                                    "birth_date": json_serial(new_birth_date),
                                    }, headers=headers)

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "James_updated"
        assert data["last_name"] == "Bond"
        assert data["email"] == "james_updated@gmail.com"
        assert data["contact_number"] == "333-333-3333"
        assert data["birth_date"] == json_serial(new_birth_date)
        assert "id" in data


"""
Оновити існуючий контакт, який не існує.
"""


def test_update_contact_not_found(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token  # Отримує токен за допомогою фікстури get_token із conftest.py
        headers = {"Authorization": f"Bearer {token}"}  # Створює заголовки з отриманим токеном для автентифікації.
        new_birth_date = datetime(2003, 4, 20)

        # Mock Rate Limiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.put("/api/contacts/9",
                              json={"first_name": "James_updated",
                                    "last_name": "Bond",
                                    "email": "james_updated_not_found@gmail.com",
                                    "contact_number": "333-333-4444",
                                    "birth_date": json_serial(new_birth_date),
                                    }, headers=headers)

        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NOT_FOUND


"""
Контакт з такою електронной поштою вже існує.
"""


def test_update_contact_email_exists(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token  # Отримує токен за допомогою фікстури get_token із conftest.py
        headers = {"Authorization": f"Bearer {token}"}  # Створює заголовки з отриманим токеном для автентифікації.
        new_birth_date = datetime(2003, 4, 20)

        # Mock Rate Limiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.put("/api/contacts/2",
                              json={"first_name": "James_updated",
                                    "last_name": "Bond",
                                    "email": "james_updated@gmail.com",
                                    "contact_number": "333-333-3333",
                                    "birth_date": json_serial(new_birth_date),
                                    }, headers=headers)

        assert response.status_code == 409, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NUMBER_EMAIL_EXISTS


"""
Контакт з таким номером телефону вже існує.
"""


def test_update_contact_number_exists(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token  # Отримує токен за допомогою фікстури get_token із conftest.py
        headers = {"Authorization": f"Bearer {token}"}  # Створює заголовки з отриманим токеном для автентифікації.
        new_birth_date = datetime(2003, 4, 20)

        # Mock Rate Limiter
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.put("/api/contacts/2",
                              json={"first_name": "James_updated",
                                    "last_name": "Bond",
                                    "email": "james_updated@gmail.com",
                                    "contact_number": "333-333-4444",
                                    "birth_date": json_serial(new_birth_date),
                                    }, headers=headers)

        assert response.status_code == 409, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NUMBER_EMAIL_EXISTS


"""
Контакти повинні бути доступні для пошуку за іменем.
"""


def test_find_by_first_name(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get(f"/api/contacts/search/?first_name=James_updated", headers=headers)
        data = response.json()
        print(f"DATA: {data}")
        assert len(data) == 1
        assert "id" in data[0]
        assert data[0]["first_name"] == "James_updated"
        assert data[0]["last_name"] == "Bond"
        assert data[0]["email"] == "james_updated@gmail.com"
        assert data[0]["contact_number"] == "333-333-3333"


"""
Контакти повинні бути доступні для пошуку за прізвищем.
"""


def test_find_by_last_name(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get(f"/api/contacts/search/?last_name=Bond", headers=headers)
        data = response.json()
        print(f"DATA: {data}")
        assert len(data) == 1
        assert "id" in data[0]
        assert data[0]["first_name"] == "James_updated"
        assert data[0]["last_name"] == "Bond"
        assert data[0]["email"] == "james_updated@gmail.com"
        assert data[0]["contact_number"] == "333-333-3333"


"""
Контакти повинні бути доступні для пошуку за електронною адресою.
"""


def test_find_by_email(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get(f"/api/contacts/search/?email=james_updated@gmail.com", headers=headers)
        data = response.json()
        print(f"DATA: {data}")
        assert "id" in data
        assert data["first_name"] == "James_updated"
        assert data["last_name"] == "Bond"
        assert data["email"] == "james_updated@gmail.com"
        assert data["contact_number"] == "333-333-3333"


"""
Параметр для пошуку не заданий.
"""


def test_find_no_parameters(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get(f"/api/contacts/search/", headers=headers)
        data = response.json()
        print(f"DATA: {data}")
        assert response.status_code == 400, response.text


"""
Отримання списку контактів з днями народження на найближчі 7 днів
"""


def test_get_upcoming_birthdays(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.get("/api/contacts/birthdays/", headers=headers)
        data = response.json()
        print(f"DATA: {data}")
        assert response.status_code == 200, response.text
        assert len(data) == 1


"""
Завантаження файлу.
"""


def test_upload_file(monkeypatch):
    client = TestClient(app)
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
    monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
    # Mocking a file with some content
    test_content = b"Test content of the file"
    test_file = BytesIO(test_content)
    test_file.name = "test_file.txt"

    # Uploading the mocked file
    files = {'file': ('test_file.txt', test_file)}
    response = client.post("api/contacts/upload-file/", files=files)

    assert response.status_code == 200, response.text
    assert 'file_path' in response.json()
    file_path = response.json()['file_path']
    assert file_path.startswith('uploads/')

    # Optionally, you can test file size limit exceeded case
    large_test_content = b"A" * (MAX_FILE_SIZE + 100)  # Generating content larger than MAX_FILE_SIZE
    large_test_file = BytesIO(large_test_content)
    large_test_file.name = "large_file.txt"

    files = {'file': ('large_file.txt', large_test_file)}
    response = client.post("api/contacts/upload-file/", files=files)

    assert response.status_code == 413, response.text


"""
Видалення контакту.
"""


def test_delete_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_cache:
        redis_cache.get.return_value = None
        token = get_token  # Отримує токен за допомогою фікстури get_token із conftest.py
        headers = {"Authorization": f"Bearer {token}"}  # Створює заголовки з отриманим токеном для автентифікації.

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.delete("/api/contacts/2", headers=headers)
        assert response.status_code == 204, response.text


"""
Видалення контакту, якого не існує.
"""


def test_repeat_delete_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'cache') as redis_cache:
        redis_cache.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        response = client.delete("/api/contacts/9", headers=headers)
        data = response.json()
        assert response.status_code == 404, response.text
        assert data["detail"] == messages.CONTACT_NOT_FOUND
