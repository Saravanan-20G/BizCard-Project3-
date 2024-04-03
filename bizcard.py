import easyocr
from PIL import Image
import io
import re
import pandas as pd
import psycopg2
import streamlit as st
from streamlit_option_menu import option_menu

mydb = psycopg2.connect(host='localhost', user='postgres', password='123456', database='bizcard', port=5432)
cursor = mydb.cursor()

reader = easyocr.Reader(['en'], gpu=False)
image_path = "C:\\Users\\Saravanan\\OneDrive\\Desktop\\Bizcard\\1.png"
image_data = reader.readtext(image_path, detail = 0)
image_data

image = Image.open(image_path)

image = image.convert('RGB')


import re

def extracted_text (image_path):
    details = reader.readtext(image_path, detail = 0)
    
    data = {
        "name": "",
        "designation": "",
        "contact": [],
        "email": "",
        "website": "",
        "address": "",
        "city": "",
        "state":"",
        "pincode": "",
        "company": "",
       
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
    # Join company names with comma and space
    data["company"] = " ".join(data["company"])
    return data

df = pd.DataFrame(data)

st.set_page_config(page_title= "BizCardX",
                   page_icon= '💼',
                   layout= "wide",)

text ='Bizcardx -- Extracting Business Card Data with OCR'  
st.markdown(f"<h2 style='color: white; text-align: center;'>{text} </h2>", unsafe_allow_html=True)

st.markdown(f""" <style>.stApp {{
                    background: url('https://img.freepik.com/free-vector/gradient-golden-luxury-business-card-template_23-2149035722.jpg?w=740&t=st=1712021022~exp=1712021622~hmac=af788945480688006d710a5bda024f6d2b87d50990c0edd91b1e0c7c4b205ddf');   
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
    if menu == 'Upload':
        upload_menu = option_menu("Upload", ['Predefined','Undefined'],                        
                        menu_icon='cloud-upload',
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

