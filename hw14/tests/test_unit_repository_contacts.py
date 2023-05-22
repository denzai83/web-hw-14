import datetime
import unittest
from unittest.mock import MagicMock
from datetime import date

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contact_by_id,
    get_contacts,
    get_contacts_birthdays,
    create_contact,
    update_contact,
    remove_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.contact_test = Contact(
            id=1,
            first_name='John',
            last_name='Doe',
            email='johndoe@mail.com',
            phone='+1234567890',
            date_of_birth=datetime.date(year=1979, month=5, day=21),
        )

    async def test_get_contacts(self):
        contacts = [self.contact_test, Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, first_name='', last_name='', email='', user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_filter_by_first_name(self):
        contacts = [self.contact_test, Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, first_name=self.contact_test.first_name, last_name='', email='', user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_filter_by_last_name(self):
        contacts = [self.contact_test, Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, first_name='', last_name=self.contact_test.last_name, email='', user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_filter_by_email(self):
        contacts = [self.contact_test, Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, first_name='', last_name='', email=self.contact_test.email, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contacts = [self.contact_test, Contact(), Contact()]
        self.session.query().filter().first.return_value = contacts
        result = await get_contact_by_id(contact_id=self.contact_test.id, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactModel(
            first_name=self.contact_test.first_name,
            last_name=self.contact_test.last_name,
            email=self.contact_test.email,
            phone=self.contact_test.email,
            date_of_birth=self.contact_test.date_of_birth,
        )
        result = await create_contact(body=body, db=self.session, user=self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact(self):
        contact = self.contact_test
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=self.contact_test.id, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=self.contact_test.id, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_update_contact(self):
        contact = self.contact_test
        body = ContactModel(
            first_name='Jonny',
            last_name=self.contact_test.last_name,
            email=self.contact_test.email,
            phone=self.contact_test.email,
            date_of_birth=self.contact_test.date_of_birth)
        self.session.query().filter().first.return_value = contact
        result = await update_contact(contact_id=self.contact_test.id, body=body, db=self.session, user=self.user)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactModel(
            first_name='Jonny',
            last_name=self.contact_test.last_name,
            email=self.contact_test.email,
            phone=self.contact_test.email,
            date_of_birth=self.contact_test.date_of_birth)
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=self.contact_test.id, body=body, db=self.session, user=self.user)
        self.assertIsNone(result)

    async def test_get_contacts_birthdays(self):
        today = date.today()
        contacts = [
            Contact(id=1, first_name='John', last_name='Doe', email='john@example.com', date_of_birth=today),
            Contact(id=2, first_name='Jane', last_name='Smith', email='jane@example.com', date_of_birth=today),
        ]
        self.session.query().filter().offset().limit().all.return_value = contacts

        result = await get_contacts_birthdays(0, 10, self.user, self.session)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()