import datetime as dt
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


# класс для работы с таблицей новостей
class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=True)
    content = sa.Column(sa.String, nullable=True)
    city = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    img = sa.Column(sa.String, nullable=True)
    created_data = sa.Column(sa.DateTime, default=dt.datetime.now)
    is_private = sa.Column(sa.Boolean, default=True)
    is_published = sa.Column(sa.Boolean, default=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("user.id"))
    # category_id = sa.Column(sa.Integer, sa.ForeignKey("category.id"))
    user = orm.relationship('User')
    categories = orm.relationship('Category', secondary='association', backref='news', lazy=True)

    def append(self, item):
        if item not in self:
            self.data.append(item)
