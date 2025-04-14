from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

db_url = 'sqlite:///bot.db'

# Create the base class for declarative models
Base = declarative_base()

class TwitterMessage(Base):
    __tablename__ = 'twitter_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    content = Column(Text, nullable=True)
    interpretation = Column(Text, nullable=True)

class DatabaseManager:
    def __init__(self, db_url=db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(self.engine)
        
    def append_message(self, message_id: str, created_at: datetime, content: str, interpretation: str = None):
        """Append a new message to the database"""
        session = self.Session()
        try:
            # Ensure created_at is a datetime object
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            message = TwitterMessage(
                message_id=message_id,
                created_at=created_at,
                content=content,
                interpretation=interpretation
            )
            session.add(message)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error appending message: {e}")
            return False
        finally:
            session.close()
            
    def get_messages(self, limit: int = 100):
        """Get the most recent messages"""
        session = self.Session()
        try:
            messages = session.query(TwitterMessage).order_by(TwitterMessage.created_at.desc()).limit(limit).all()
            return messages
        finally:
            session.close()
            
    def get_message_by_id(self, message_id: str):
        """Get a specific message by its ID"""
        session = self.Session()
        try:
            message = session.query(TwitterMessage).filter_by(message_id=message_id).first()
            return message
        finally:
            session.close() 
    
    def get_all_messages_ids(self):
        """Get all messages IDs"""
        session = self.Session()
        try:
            messages = session.query(TwitterMessage).all()
            return [message.message_id for message in messages]
        finally:
            session.close() 
            
    def get_not_interpreted_messages(self, limit: int = 10):
        """Get messages that don't have an interpretation yet"""
        session = self.Session()
        try:
            messages = session.query(TwitterMessage).filter(
                TwitterMessage.interpretation.is_(None)
            ).order_by(TwitterMessage.created_at.desc()).limit(limit).all()
            return messages
        finally:
            session.close()
            
    def update_interpretation(self, message_id: str, interpretation: str):
        """Update the interpretation of a message"""
        session = self.Session()
        try:
            message = session.query(TwitterMessage).filter_by(message_id=message_id).first()
            if message:
                message.interpretation = interpretation
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error updating interpretation: {e}")
            return False
        finally:
            session.close() 
