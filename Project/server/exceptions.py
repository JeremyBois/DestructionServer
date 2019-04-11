# exceptions.py

from sqlalchemy.exc import IntegrityError


class TableNameError(KeyError):

    def __init__(self, *args):

        # Call the base class constructor with the parameters it needs
        super(TableNameError, self).__init__(*args)


class ForeignKeyError(IntegrityError):

    def __init__(self, *args):

        # Call the base class constructor with the parameters it needs
        super(ForeignKeyError, self).__init__(*args)
