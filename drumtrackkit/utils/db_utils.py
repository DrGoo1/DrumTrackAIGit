import logging
from contextlib import contextmanager
from drumtrackkit import db

# Set up logging
logger = logging.getLogger(__name__)

@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    Usage:
        with session_scope() as session:
            session.add(my_object)
            # No need to call session.commit()
    """
    session = db.Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        session.rollback()
        raise
    finally:
        session.close()