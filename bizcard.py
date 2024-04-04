import streamlit as st
import psycopg2
import easyocr
from PIL import Image
import io

# Function to create PostgreSQL database table if it doesn't exist
def create_table():
    conn = psycopg2.connect(
        host="localhost",
        database="bizcard",
        user="postgres",
        password="123456"
    )
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS business_cards
                 (id SERIAL PRIMARY KEY,
                 company TEXT,
                 name TEXT,
                 designation TEXT,
                 contact TEXT,
                 email TEXT,
                 website TEXT,
                 area TEXT,
                 city TEXT,
                 state TEXT,
                 pincode TEXT,
                 image BYTEA)''')
    conn.commit()
    conn.close()

# Function to save business card data to PostgreSQL database
def save_to_database(data, image):
    conn = psycopg2.connect(
        host="localhost",
        database="bizcard",
        user="postgres",
        password="123456"
    )
    c = conn.cursor()
    c.execute('''INSERT INTO business_cards (company, name, designation, contact, email, website, area, city, state, pincode, image)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', data)
    conn.commit()
    conn.close()

# Function to extract text from image using easyOCR
def extract_text(image):
    reader = easyocr.Reader(['en'])
    
    # Convert image to RGB format (if RGBA)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Convert image to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes = image_bytes.getvalue()
    
    # Extract text from the image bytes
    result = reader.readtext(image_bytes)
    return result

# Function to display saved data and allow update and delete operations
def display_saved_data():
    conn = psycopg2.connect(
        host="localhost",
        database="bizcard",
        user="postgres",
        password="123456"
    )
    c = conn.cursor()
    c.execute('''SELECT * FROM business_cards''')
    rows = c.fetchall()
    conn.close()

    st.subheader('Saved Data:')
    for row in rows:
        st.write(f"ID: {row[0]}, Company: {row[1]}, Name: {row[2]}, Designation: {row[3]}, Contact: {row[4]}, Email: {row[5]}, Website: {row[6]}, Area: {row[7]}, City: {row[8]}, State: {row[9]}, Pincode: {row[10]}")
        if st.button(f"Update {row[0]}"):
            update_data(row[0])
        if st.button(f"Delete {row[0]}"):
            delete_data(row[0])

# Function to update data
def update_data(id):
    # Implement update logic here
    st.write(f"Updating data for ID: {id}")

# Function to delete data
def delete_data(id):
    # Implement delete logic here
    st.write(f"Deleting data for ID: {id}")

# Streamlit UI
def main():
    st.title("BizCardX: Extracting Business Card Data with OCR")

    # Create sidebar with dropdown options
    st.sidebar.title('Options')
    selected_option = st.sidebar.selectbox('Select Option', ['Home', 'Upload', 'Extract', 'Modify', 'Delete'])

    if selected_option == 'Upload':
        # File uploader
        uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "png", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)

            if st.button('Extract Information'):
                # Extract text from the uploaded image
                extracted_text = extract_text(image)

                # Display extracted information
                st.subheader('Extracted Information:')
                for item in extracted_text:
                    st.write(item[1])

                # Convert image to bytes
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG')
                image_bytes = image_bytes.getvalue()

                # Save extracted information to PostgreSQL database
                save_to_database(extracted_text, image_bytes)
                st.success('Information saved to database successfully.')

    elif selected_option == 'Extract':
        # Display saved data and allow update and delete operations
        display_saved_data()

# Create PostgreSQL database table
create_table()

# Run Streamlit app
if __name__ == "__main__":
    main()
