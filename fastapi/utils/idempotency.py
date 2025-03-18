# from sqlmodel import Session
# from datetime import datetime, timedelta, timezone
# from main import db_engine 
# from db.models import IdempotencyKey


# def clean_old_idempotency_keys():
#     with Session(db_engine) as session:
#         # Get the current date and time minus 1 day, with UTC timezone
#         cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)

#         # Use SQLModel's ORM to query and delete the records
#         expired_keys = session.query(IdempotencyKey).filter(IdempotencyKey.created_at < cutoff_time).all()
        
#         # If expired keys exist, delete them
#         if expired_keys:
#             for key in expired_keys:
#                 session.delete(key)
            
#             session.commit()
#             print(f"Cleaned up {len(expired_keys)} idempotency keys older than {cutoff_time}")
#         else:
#             print("No idempotency keys to clean.")