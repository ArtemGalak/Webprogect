import sqlalchemy
from .db_session import SqlAlchemyBase


class Calls(SqlAlchemyBase):
    __tablename__ = 'calls'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    message = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_done = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)