# Package
# image_processing

import easyocr
from PIL import Image
import re

# database

import pandas as pd
from sqlalchemy import create_engine, update, MetaData, Table
from sqlalchemy import Column, Integer, String

# app

import os
import streamlit as st
from streamlit_option_menu import option_menu


# Creating a database engine
engine = create_engine("postgresql+psycopg2://postgres:123456@localhost/bizcard")

# Creating a connection
connection = engine.connect()

# Reflecting the existing database schema
metadata = MetaData()
metadata.reflect(bind=engine)

# Accessing the 'business_card' table from the reflected metadata
#business_card_table = Table('business_card', metadata, autoload=True, autoload_with=engine)



# Define the structure of the 'business_card' table
# Define the structure of the 'business_card' table
business_card_table = Table(
    'business_card', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('designation', String),
    Column('contact', String),
    Column('email', String),
    Column('website', String),
    Column('street', String),
    Column('city', String),
    Column('state', String),
    Column('pincode', String),
    Column('company', String),
    extend_existing=True  # Specify extend_existing=True
)


# Extracting text from image
def extract_text(image_path):
    reader = easyocr.Reader(['en'], gpu=False)
    image = Image.open(image_path).convert('RGB')
    details = reader.readtext(image_path, detail=0)
    return details

#Processing text details
def process_text(details):
    data = {
        "name": "",
        "designation": "",
        "contact": [],
        "email": "",
        "website": "",
        "street": "",
        "city": "",
        "state": "",
        "pincode": "",
        "company": []
    }

    for i in range(len(details)):
        match1 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+). ([a-zA-Z]+)', details[i])
        match2 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+)', details[i])
        match3 = re.findall('^[E].+[a-z]', details[i])
        match4 = re.findall('([A-Za-z]+) ([0-9]+)', details[i])
        match5 = re.findall('([0-9]+ [a-zA-z]+)', details[i])
        match6 = re.findall('.com$', details[i])
        match7 = re.findall('([0-9]+)', details[i])
        if i == 0:
            data["name"] = details[i]
        elif i == 1:
            data["designation"] = details[i]
        elif '-' in details[i]:
            data["contact"].append(details[i])
        elif '@' in details[i]:
            data["email"] = details[i]
        elif "www " in details[i].lower() or "www." in details[i].lower():
            data["website"] = details[i]
        elif "WWW" in details[i]:
            data["website"] = details[i] + "." + details[i+1]
        elif match6:
            pass
        elif match1:
            data["street"] = match1[0][0]
            data["city"] = match1[0][1]
            data["state"] = match1[0][2]
        elif match2:
            data["street"] = match2[0][0]
            data["city"] = match2[0][1]
        elif match3:
            data["city"] = match3[0]
        elif match4:
            data["state"] = match4[0][0]
            data["pincode"] = match4[0][1]
        elif match5:
            data["street"] = match5[0] + ' St,'
        elif match7:
            data["pincode"] = match7[0]
        else:
            data["company"].append(details[i])

    data["contact"] = " & ".join(data["contact"])
    # Joining company names with space
    data["company"] = " ".join(data["company"])
    return data

#Extract the  data
def store_data(data):
    # Converting dictionary to DataFrame
    df = pd.DataFrame([data]) # Wrap data in a list to create DataFrame
    # Storing DataFrame in SQL table
    df.to_sql('business_card', engine, if_exists='append', index=False)
    return df


# Streamlit part

text = 'BizCardX'   
st.markdown(f"<h2 style='color: white; text-align: center;'>{text} </h2>", unsafe_allow_html=True)

st.markdown(f""" <style>.stApp {{
                    background: url('https://tse4.mm.bing.net/th?id=OIP.Dj6ezrB9q7wLkzTePKE64AHaEo&pid=Api&P=0&h=220');   
                    background-size: cover}}
                 </style>""",unsafe_allow_html=True)

col1,col2 = st.columns([1,4])
with col1:
    menu = option_menu("Menu", ["Home","Upload","Database"], 
                    icons=["house",'cloud-upload', "list-task"],
                    menu_icon="cast",
                    default_index=0,
                    styles={"icon": {"color": "orange", "font-size": "20px"},
                            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "-2px", "--hover-color": "#FFFFFF"},
                            "nav-link-selected": {"background-color": "#225154"}})
    if menu == 'Database':
        Database_menu = option_menu("Database", ['Modify','Delete'], 
                        
                        menu_icon="list-task",
                        default_index=0,
                        styles={"icon": {"color": "orange", "font-size": "20px"},
                                "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "--hover-color": "#FFFFFF"},
                                "nav-link-selected": {"background-color": "#225154"}})



with col2:
    if menu == 'Home':
        st.header('Welcome to BizCardX')
        home_text = ('This app  extract and manage business card details')
        st.markdown(f"<h4 text-align: left;'>{home_text} </h4>", unsafe_allow_html=True)
      
        st.subheader(":orange[Technologies Used:]")
        tech_text =(''' Python
                        Streamlit
                        easyOCR
                        Postgres''')
        st.markdown(f"<h4 text-align: left;'>{tech_text} </h4>", unsafe_allow_html=True)


    if menu == 'Upload':
        path = False
    col3, col4 = st.columns([2, 2])
    upload = False  # Define the 'upload' variable here with an initial value
    with col3:
        uploaded_file = st.file_uploader("**Choose a file**", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            image_path = os.getcwd() + "\\" + "bizcards" + "\\" + uploaded_file.name
            image = Image.open(image_path)
            col3.image(image)
            path = True

            extract = st.button("Extract")
            upload = st.button("Upload")  # Assign a value to 'upload' variable here
            if upload:
                if path:
                    image_details = extract_text(image_path)
                    processed_details = process_text(image_details)
                    df = store_data(processed_details)
                    st.write(df)
                    st.success("Uploaded successfully")

    with col4:
        st.info('''i) Kindly upload the image in JPG, PNG, or JPEG format.       
                ii) Click the "**Extract**" button to extract text from the image.              
                iii) Click the "**Upload**" upload the extracted text details to the database. ''', icon="ℹ️")
        if path:
            if extract:
                image_details = extract_text(image_path)
                processed_details = process_text(image_details)
                st.write('**Name** :', processed_details['name'])
                st.write('**Designation** :', processed_details['designation'])
                st.write('**Company Name** :', processed_details['company'])
                st.write('**Contact Number** :', processed_details['contact'])
                st.write('**E-mail** :', processed_details['email'])
                st.write('**Website** :', processed_details['website'])
                st.write('**Street** :', processed_details['street'])
                st.write('**City** :', processed_details['city'])
                st.write('**State** :', processed_details['state'])
                st.write('**Pincode** :', processed_details['pincode'])


    if Database_menu == 'Database':
    # Read data from the 'business_card' table into a DataFrame
        try:
            df = pd.read_sql('SELECT * FROM business_card', engine)
            st.header("Database")                    
            st.dataframe(df)
            st.button('Show Changes')
        except Exception as e:
            st.error(f"Failed to read data from the database: {str(e)}")
        finally:
        # Close the database connection
            connection.close()


        if Database_menu == 'Modify':
            modify_col_1,modify_col_2 = st.columns([1,1])
            with modify_col_1:
                st.header('Choose where to modify the details.')
                names= ['Please select one','name','contact','email']
                selected = st.selectbox('**Select Categories**',names)
                if selected != 'Please select one':
                        select = ['Please select one'] + list(df[selected])
                        select_detail = st.selectbox(f'**Select the {selected}**', select)
                        
                        with modify_col_2:
                            if select_detail != 'Please select one':
                                st.header('Choose what details to modify.')
                                df1 = df[df[selected] == select_detail]
                                df1 = df1.reset_index()
                                select_modify = st.selectbox('**Select categories**', ['Please select one'] + list(df.columns))
                                if select_modify != 'Please select one':
                                    a = df1[select_modify][0]            
                                    st.write(f'Do you want to change {select_modify}: **{a}** ?')
                                    modified = st.text_input(f'**Enter the {select_modify} to be modified.**')
                                    if modified:
                                        st.write(f'{select_modify} **{a}** will change as **{modified}**')
                                        with modify_col_1:
                                            if st.button("Commit Changes"):
                                                # Define the update statement
                                                update_statement = (
                                                                    update(business_card_table)
                                                                    .where(business_card_table.c[selected] == select_detail)
                                                                    .values({select_modify: modified})
                                                                )
                                                # Executing the update statement
                                                connection.execute(update_statement)
                                                connection.commit()
                                                st.success("Changes committed successfully!")
            
        if Database_menu == 'Delete':
            names= ['Please select one','name','email']
            delete_selected = st.selectbox('**Select where to delete the details**',names) 
            if delete_selected != 'Please select one':
                select = df[delete_selected]
                delete_select_detail = st.selectbox(f'**Select the {delete_selected} to remove**', ['Please select one'] + list(select))
                if delete_select_detail != 'Please select one':
                    st.write(f'Do you want to delete **{delete_select_detail}** card details ?')
                    col5,col6,col7 =st.columns([1,1,5])
                    delete = col5.button('Yes I do')
                    if delete:
                        delete_query = (
                                        business_card_table.delete()
                                        .where(business_card_table.c[delete_selected] == delete_select_detail)
                                        )

                        # Execute the delete statement
                        connection.execute(delete_query)
                        connection.commit()
                        st.success("Data Deleted successfully", icon ='✅')
                   
            
                                                                        
