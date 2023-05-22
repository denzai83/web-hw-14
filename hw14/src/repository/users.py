from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session):
    """
    The get_user_by_email function takes in an email and a database session, then returns the user with that email.
    
    :param email: str: Pass the email of the user to be searched for
    :param db: Session: Connect to the database
    :return: The first user that matches the email address
    :doc-author: Trelent
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session):
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserModel): The UserModel object to be created.
            db (Session): The SQLAlchemy session object used for querying the database.
    
    :param body: UserModel: Pass the user model to the function
    :param db: Session: Create a session with the database
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session):
    """
    The update_token function updates the refresh_token for a user.
    
    :param user: User: Identify the user that is being updated
    :param token: str | None: Pass in the token that is returned from the database
    :param db: Session: Commit the changes to the database
    :return: Nothing
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.
    
    :param email: str: Specify the email of the user that is being confirmed
    :param db: Session: Access the database
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    :param email: The email address of the user to update
    :param url: str: Pass the url of the avatar to be updated
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user