import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f=open("books.csv")
reader=csv.reader(f)

db.execute('''CREATE TABLE IF NOT EXISTS Books(
    ISBN VARCHAR NOT NULL PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year VARCHAR NOT NULL 
)''')
db.commit()
    

for ISBN,title,author,year in reader:
    db.execute("INSERT INTO Books(ISBN,title,author,year) VALUES(:ISBN,:title,:author,:year)",
    {"ISBN":ISBN,"title":title,"author":author,"year":year})
    print("inserted ISBN:%s,title:%s,author:%s,year:%s"%(ISBN,title,author,year))

db.commit()


