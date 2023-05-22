import pickle
import redis
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.config.config import settings


class Auth:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and the hashed version of that password,
            and returns True if they match, False otherwise. This is used to verify that the user's login
            credentials are correct.
        
        :param self: Represent the instance of the class
        :param plain_password: Check the password that is entered by the user
        :param hashed_password: Verify the plain_password parameter
        :return: A boolean value
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
            The function uses the pwd_context object to generate a hash from the given password.
        
        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is to be hashed
        :return: The hashed password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token for the user.
            The function takes in two arguments: data and expires_delta. Data is a dictionary that contains all of the information about the user, such as their username, email address, etc. Expires_delta is an optional argument that specifies how long you want your access token to be valid for (in minutes). If no value is specified then it defaults to 120 minutes (2 hours).
            The function first creates a copy of the data dictionary called to_encode and adds three additional key-value pairs: iat which stands for issued at time and represents when

        :param self: Refer to the current object
        :param data: dict: Pass the data that will be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A string that is the encoded access token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data to be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time for the refresh token
        :return: A refresh token that is encoded with the user's id, email and username
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function takes a refresh token and decodes it.
            If the scope is 'refresh_token', then we return the email address of the user.
            Otherwise, we raise an HTTPException with status code 401 (UNAUTHORIZED) and detail message 'Invalid scope for token'.
        
        
        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token that is sent by the client
        :return: The email of the user who requested a refresh token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the protected routes.
        It takes an access token as input and returns the user object if it's valid, otherwise raises an exception.
        
        :param self: Represent the instance of a class
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: The user object, but the function is async
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.r.get(f'user:{email}')
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f'user:{email}', pickle.dumps(user))
            self.r.expire(f'user:{email}', 900)
        else:
            user = pickle.loads(user)
        return user
    
    def create_email_token(self, data: dict):
        """
        The create_email_token function takes a dictionary of data and returns a token.
            The token is encoded with the SECRET_KEY and ALGORITHM defined in the class.
            The dictionary passed to this function should contain at least an email key, 
            but can also include other keys that will be included in the payload of the JWT.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into a token
        :return: A token that is encoded with the user's email, a timestamp, and an expiration date
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    
    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
            If the token is invalid, it raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Pass the token to the function
        :return: The email address of the user who requested the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload['sub']
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid token for email verification')


auth_service = Auth()
