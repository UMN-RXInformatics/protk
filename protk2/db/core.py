"""
protk2.db.core : Core database types and functions
"""

from sqlalchemy import create_engine
import types
from types import *

class DBConfError(Exception):
    pass
class DBDriverError(Exception):
    pass
class DBEngineError(Exception):
    pass

"""
DATABASE ENGINE
"""
def get_engine(dbconf):
    
    # Verify that an actual database configuration was passed in
    if not dbconf:
        raise DBConfError("Please provide a database configuration")
    
    # Check for a driver key
    if dbconf.has_key('driver'):
        if dbconf['driver'] == 'sqlite3' and dbconf.has_key('name'):
            # Try to create the engine and raise an error if it can't be created
            try:
                z = create_engine('sqlite:///%s' % dbconf['name'])
                return z
            except Exception:
                raise DBEngineError("Could not create the database engine. Check configuration")
    # Raise an error if no driver is specified
    else:
        raise DBDriverError("A database driver was not specified.")

"""
DATABASE SESSION
"""
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
session_configured = False

def get_session(dbconf):
    """
    Get a session hand to the current database
    """
    global Session
    global session_configured
    if not session_configured:
        engine = get_engine(dbconf)
        #create_db(engine)
        Session.configure(bind=engine)
        session_configured=True
    return Session()
              
class DatabaseManager(object):
    
    def __init__(self, configuration):
        self.configuration = configuration
        self.engine = get_engine(configuration)
        self.sessionmaker = sessionmaker()
        self.sessionmaker.configure(bind=self.engine)
        self.session = None
        
    def get_session(self):
        if self.session == None:
            self.session = self.sessionmaker()
        return self.session
    
    def initialize_db(self, base):
        if not self.engine:
            self.engine = get_engine(self.configuration)
        base.metadata.create_all(self.engine)
        
    