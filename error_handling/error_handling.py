import asyncio
import discord

from sqlalchemy import exc

'''
Handles all the possible errors with decorators and defined functions for returned False
'''

def database_error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        except exc.AmbiguousForeignKeysError:
            # Error 1
        except exc.ArgumentError:
            # ArgumentError
        except exc.CircularDependencyError:
            # CircularDependencyError
        except exc.ConstraintColumnNotFoundError:
            # ConstraintColumnNotFoundError
        except exc.DataError:
            # DataError
        except exc.DatabaseError:
            # DatabaseError
        except exc.IdentifierError:
            # IdentifierError. Beyond the character limit
        except exc.IllegalStateChangeError:
            # IllegalStateChangeError
        except exc.IntegrityError:
            # IntegrityError
        except exc.InterfaceError:
            # InterfaceError
        except exc.InternalError:
            # InternalError
        except exc.NoSuchColumnError:
            # NoSuchColumnError. Table column not found
        except exc.NoSuchTableError:
            # NoSuchTableError. Table not found
            '''TODO
            - Add all the other sqlalchemy availably core error handling
            '''
        except Exception as e:
            print("This error cannot be handled. Error is:\n{}".format(e))
