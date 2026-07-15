from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:Aravind1234@localhost:5432/enterprise_ai"

engine = create_engine(DATABASE_URL)

connection = engine.connect()

print("Database Connected Successfully")