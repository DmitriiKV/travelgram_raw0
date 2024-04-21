import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

association_table = sa.Table('association', SqlAlchemyBase.metadata,
                             sa.Column('news', sa.Integer, sa.ForeignKey('news.id')),
                             sa.Column('category', sa.Integer, sa.ForeignKey('category.id')))


# класс для работы с таблицей категорий
class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column(sa.String, nullable=False)
