import re

from ..extensions.database import db


class CaseConverter:
    @staticmethod
    def camel_to_snake(string):
        string = string[0].upper() + string[1:]
        converted = re.sub(
            r"([A-Z]+)([A-Z][a-z])",
            r"\1_\2",
            re.sub(r"([A-Z]+[a-z]+)(?=([A-Z]))", r"\1_", string)
        ).lower()

        return converted

    @staticmethod
    def snake_to_camel(string, pascal=True):
        converted = "".join([s[0].upper() + s[1:] for s in string.split("_")])

        if not pascal:
            converted = converted[0].lower() + converted[1:]

        return converted


class Model(db.Model):
    __abstract__ = True
    __table_args__ = ({},)

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)

    @db.declared_attr
    def __tablename__(cls):
        return CaseConverter.camel_to_snake(cls.__name__) + 's'

    @classmethod
    def _create_relationship(
        cls, primary, secondary=None, backref_name=None, backref_order_by=None, backref_uselist=None, **other_kwargs
    ):
        if backref_name is None:
            backref_name = cls.__tablename__

        if backref_order_by is None:
            backref_order_by = cls.id

        backref_kwargs = {
            "order_by": backref_order_by,
            "uselist": backref_uselist
        }
        kwargs = {"backref": db.backref(backref_name, **backref_kwargs)}
        kwargs.update(**other_kwargs)

        if secondary is not None:
            kwargs["secondary"] = secondary

        return db.relationship(primary, **kwargs)

    @classmethod
    def _update_table_args(cls, *args, **kwargs):
        cur_table_args = cls.__table_args__

        if isinstance(cur_table_args[0], dict):
            cur_args = []
        else:
            cur_args = list(cur_table_args[:-1])

        cur_kwargs = cur_table_args[-1]

        if args:
            cur_args.extend(args)
        if kwargs:
            cur_kwargs.update(kwargs)

        cur_args.append(cur_kwargs)

        return tuple(cur_args)

    @classmethod
    def create(cls, commit=True, *args, **kwargs):
        instance = cls(*args, **kwargs)
        instance.save(commit=commit)

        return instance

    @classmethod
    def get(cls, cond):
        return cls.query.filter(cond).first()

    @classmethod
    def get_by(cls, cond_dict):
        return cls.query.filter_by(**cond_dict).first()

    @classmethod
    def get_or_create(cls, cond, commit=True, *args, **kwargs):
        obj = cls.get(cond)

        if not obj:
            obj = cls.create(commit=commit, *args, **kwargs)

        return obj

    @classmethod
    def get_by_or_create(cls, cond_dict, commit=True, *args, **kwargs):
        obj = cls.get_by(cond_dict)

        if not obj:
            obj = cls.create(commit=commit, *args, **kwargs)

        return obj

    def __str__(self):
        return f"{self.__class__.__name__}(id={repr(self.id)})"

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

        if commit:
            db.session.commit()

    def save(self, commit=True):
        db.session.add(self)

        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)

        if commit:
            db.session.commit()


def create_secondary_table(name, model1, model2, *args, model1_id=None, model2_id=None, unique=True):
    if not model1_id:
        model1_id = f"{model1.__name__.lower()}_id"

    if not model2_id:
        model2_id = f"{model2.__name__.lower()}_id"

    table_args = [
        name,
        db.Column("id", db.Integer(), primary_key=True, autoincrement=True),
        db.Column(model1_id, db.Integer(), db.ForeignKey(model1.id), index=True, nullable=False),
        db.Column(model2_id, db.Integer(), db.ForeignKey(model2.id), index=True, nullable=False)
    ]
    table_args.extend(args)

    if unique:
        table_args.append(db.UniqueConstraint(model1_id, model2_id))

    return db.Table(*table_args)
