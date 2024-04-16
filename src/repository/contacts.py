from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.entity.models import Contact, User
from src.schemas.schemas import ContactModel

"""
Отримати список всіх контактів.
"""


async def get_contacts(limit: int, offset: int, db: AsyncSession, current_user: User) -> list[Contact]:
    """
    The get_contacts function returns a list of contacts for the current user.
        
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass in the database connection to the function
    :param current_user: User: Filter the contacts by user
    :return: A list of contact
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    result = await db.execute(search)
    contact = result.scalars().all()
    return contact  # noqa


"""
Отримати список всіх контактів. all: role
"""


async def get_all_contacts(limit: int, offset: int, db: AsyncSession) -> list[Contact]:
    """
    The get_all_contacts function returns a list of all contacts in the database.
        
    
    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first n rows
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    search = select(Contact).offset(offset).limit(limit)
    result = await db.execute(search)
    contact = result.scalars().all()
    return contact  # noqa


"""
Створити новий контакт.
"""


async def create_contact(body: ContactModel, current_user: User, db: AsyncSession) -> Contact:
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Get the data from the request body
    :param current_user: User: Get the user that is currently logged in
    :param db: AsyncSession: Access the database
    :return: An object of type contact
    :doc-author: Trelent
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        contact_number=body.contact_number,
        birth_date=body.birth_date,
        additional_information=body.additional_information,
        user=current_user
    )

    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


"""
Отримати один контакт за ідентифікатором.
"""


async def get_contact(contact_id: int, current_user: User, db: AsyncSession) -> Contact:
    """
    The get_contact function returns a contact object from the database.
        Args:
            contact_id (int): The id of the contact to be retrieved.
            current_user (User): The user who is making this request.
            db (AsyncSession): An async session for querying the database.
    
    :param contact_id: int: Specify the id of the contact to be retrieved
    :param current_user: User: Ensure that the user is only able to get contacts that they own
    :param db: AsyncSession: Pass the database session to the function
    :return: The contact object if it exists
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(search)
    contact = result.scalar_one_or_none()
    return contact


"""
Оновити існуючий контакт.
"""


async def update_contact(contact_id: int, body: ContactModel, current_user: User, db: AsyncSession) -> Contact | None:
    """
    The update_contact function updates a contact in the database.
    
    :param contact_id: int: Identify the contact to update
    :param body: ContactModel: Get the data from the request body
    :param current_user: User: Ensure that the user is only updating their own contacts
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object, but i am not sure how to get the id from that
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(search)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.contact_number = body.contact_number
        contact.birth_date = body.birth_date
        contact.additional_information = body.additional_information
        await db.commit()
        await db.refresh(contact)
    return contact


"""
Видалити контакт.
"""


async def remove_contact(contact_id: int, current_user: User, db: AsyncSession) -> Contact | None:
    """
    The remove_contact function removes a contact from the database.
    
    :param contact_id: int: Identify the contact to be removed
    :param current_user: User: Ensure that the contact being deleted belongs to the user making the request
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(id=contact_id, user=current_user)
    result = await db.execute(search)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


"""
Пошук контакту за ім'ям.
"""


async def find_contact_by_first_name(contact_first_name: str, current_user: User, db: AsyncSession) -> list[Contact]:
    """
    The find_contact_by_first_name function searches for a contact by first name.
    
    :param contact_first_name: str: Search for a contact by first name
    :param current_user: User: Get the current user from the database
    :param db: AsyncSession: Connect to the database
    :return: A list of contact objects
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(first_name=contact_first_name, user=current_user)
    result = await db.execute(search)

    try:
        contacts = result.scalars().all()
        if not contacts:
            raise NoResultFound
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contacts  # noqa


"""
Пошук контакту за прізвищем.
"""


async def find_contact_by_last_name(contact_last_name: str, current_user: User, db: AsyncSession) -> list[Contact]:
    """
    The find_contact_by_last_name function searches for a contact by last name.
        Args:
            contact_last_name (str): The last name of the desired contact.
            current_user (User): The user who is making the request. This is used to ensure that only contacts belonging to this user are returned in the response.
    
    :param contact_last_name: str: Search for a contact by last name
    :param current_user: User: Get the current user
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(last_name=contact_last_name, user=current_user)
    result = await db.execute(search)

    try:
        contacts = result.scalars().all()
        if not contacts:
            raise NoResultFound
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contacts  # noqa


"""
Пошук контакту за електронною поштою.
"""


async def find_contact_by_email(contact_email: str, current_user: User, db: AsyncSession) -> Contact:
    """
    The find_contact_by_email function searches for a contact by email address.
        Args:
            contact_email (str): The email address of the desired Contact.
            current_user (User): The User who is making the request. This is used to ensure that only Contacts belonging to this user are returned.
            db (AsyncSession): An async database session object, which will be used to execute queries against the database and return results.
    
    :param contact_email: str: Find the contact by email
    :param current_user: User: Ensure that the user is only able to access their own contacts
    :param db: AsyncSession: Pass the database session to the function
    :return: The contact object
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(email=contact_email, user=current_user)
    result = await db.execute(search)

    try:
        contact = result.scalar()
        if not contact:
            raise NoResultFound
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return contact  # noqa


"""
API повинен мати змогу отримати список контактів з днями народження на найближчі 7 днів.
"""


async def upcoming_birthdays(current_date, to_date, skip: int, limit: int, current_user: User, db: AsyncSession) -> \
        list[Contact]:
    """
    The upcoming_birthdays function returns a list of contacts whose birthdays fall between the current date and the to_date.
    The skip and limit parameters are used for pagination.
    
    :param current_date: Get the current date
    :param to_date: Calculate the upcoming birthdays
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param current_user: User: Pass the current user to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contacts that have birthdays between the current date and the to_date
    :doc-author: Trelent
    """
    search = select(Contact).filter_by(user=current_user).offset(skip).limit(limit)
    result = await db.execute(search)
    contacts = result.scalars()

    upcoming = []

    for contact in contacts:

        contact_birthday_month_day = (contact.birth_date.month, contact.birth_date.day)
        current_date_month_day = (current_date.month, current_date.day)
        to_date_month_day = (to_date.month, to_date.day)

        if current_date_month_day < contact_birthday_month_day <= to_date_month_day:
            upcoming.append(contact)

    return upcoming
