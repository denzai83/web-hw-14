import datetime
import unittest
from unittest.mock import MagicMock


from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username='User1',
            email='user1@gmail.com',
            password='qwerty',
            confirmed=True,
        )
        self.contact_test = Contact(
            id=1,
            first_name='John',
            last_name='Doe',
            email='johndoe@mail.com',
            phone='+1234567890',
            date_of_birth=datetime.date(year=1979, month=5, day=21),
        )

    async def test_get_user_by_email(self):
        user = self.user
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password,
        )
        result = await create_user(body=body, db=self.session)

        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_confirmed_email(self):
        result = await confirmed_email(email=self.user.email, db=self.session)
        self.assertIsNone(result)

    async def test_update_token(self):
        user = self.user
        token = None
        result = await update_token(user=user, token=token, db=self.session)
        self.assertIsNone(result)

    async def test_update_avatar(self):
        new_avatar_url = 'https://res.cloudinary.com/dspp4i41l/image/upload/c_fill,h_250,w_250/v1684086359/ContactsApp/User1'
        get_user_by_email_mock = self.session.query().filter().first
        get_user_by_email_mock.return_value = self.user
        result = await update_avatar(email=self.user.email, url=new_avatar_url, db=self.session)
        self.assertEqual(result.avatar, new_avatar_url)



if __name__ == '__main__':
    unittest.main()