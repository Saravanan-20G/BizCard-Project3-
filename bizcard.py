import easyocr
from PIL import Image
import io
import re
import pandas as pd
import psycopg2

mydb = psycopg2.connect(host='localhost', user='postgres', password='123456', database='bizcard', port=5432)
cursor = mydb.cursor()

def details_table():
    create_query='''create table if not exists image(
                                                    id int primary key,
                                                    name varchar(70),
                                                    designation varchar(100),
                                                    contact varchar(50),
                                                    email varchar(50),
                                                    website varchar(75),
                                                    address varchar(200),
                                                    city varchar(50),
                                                    state varchar(50),
                                                    pincode varchar(50),
                                                    company varchar(75),
                                                    image BYTEA

    )'''
    cursor.execute(create_query)
    mydb.commit()