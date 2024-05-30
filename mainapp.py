import streamlit as st
import cv2
import easyocr
import numpy as np
import csv


reader = easyocr.Reader(['en'])
kernel = np.ones((5, 5), np.uint8)

def read_csv(filename):
    data = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data[row[0]] = row[1:]
    return data

def check_csv_for_number(number, csv_data):
    if number in csv_data:
        return csv_data[number]
    else:
        return None

def detect_number_plate(image):
    # Convert image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

    img_erosion = cv2.erode(binary_image, kernel, iterations=1)

    st.image(img_erosion, caption='blackandwhite Image', use_column_width=True)

    # Perform text detection
    result = reader.readtext(gray_image)

    # Extract detected text from result
    detected_text = [box[1] for box in result]

    return detected_text, result

def upload_page(csv_data):
    st.title("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = np.array(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # Display uploaded image
        st.image(image, caption='Uploaded Image', use_column_width=True)

        if st.button("Detect Number Plate"):
            detected_text, result = detect_number_plate(image)
            # st.write("Detected text:", detected_text)
            combined_text = " ".join(detected_text)
            # st.write(combined_text)

            # Display image with detected text
            for detection in result:
                top_left = tuple(int(coord) for coord in detection[0][0])
                bottom_right = tuple(int(coord) for coord in detection[0][2])
                text = detection[1]
                cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            st.image(image, caption='Image with Detected Text', use_column_width=True)

            normal_register_number = ""
            unique_number = ""
            if 'IND' in combined_text:
                st.success("The given number plate is an HSRP number plate")
                for text in detected_text:
                    if len(text) == 10 and text.isdigit():  # Assuming the normal register number has 10 digits
                        normal_register_number = text
                    elif text.isalnum() and any(char.isdigit() for char in text) and any(char.isalpha() for char in text):  # Unique number contains both alphabets and digits
                        unique_number = text
                if unique_number:
                    st.write("Unique Number:", unique_number)
                    values = check_csv_for_number(unique_number, csv_data)
                    if values:
                        st.write("Details of the given Number plate are as follows : ")
                        st.write("reg_no:", values[0])
                        st.write("owner :", values[1])
                        st.write("Chassis_no:", values[2])
                        st.write("ENGINE_NO:", values[3])
                        
                        st.write("ADDRESS:", values[4])
                       # st.write("PHONE NUMBER:", values[5])
                       

                    else:
                        st.write("No Data found in database.")
                else:
                    st.error("Unique number not detected.")
            else:
                st.error("The given number plate is not an HSRP number plate")
                st.text("No Data found in database.")
            

def webcam_page(csv_data):
    st.title("Capture via Webcam")
   
    st.write("Press the button below to open the webcam and capture an image:")
    capture = st.button("Open Webcam")

    if capture:
        cap = cv2.VideoCapture(1)
        st.text("Press 'Space' to capture an image.")

        while True:
            ret, frame = cap.read()
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord(' '):
                cv2.imwrite("webcam_capture.jpg", frame)
                break

        cap.release()
        cv2.destroyAllWindows()

        st.success("Image captured successfully!")
        st.write("Proceed to detect the number plate.")
        image = cv2.imread("webcam_capture.jpg")
        st.image(image, caption='Captured Image', use_column_width=True)

        detect_and_display_number_plate(image, csv_data)

def detect_and_display_number_plate(image, csv_data):
    detected_text, result = detect_number_plate(image)
    combined_text = " ".join(detected_text)

    for detection in result:
        top_left = tuple(int(coord) for coord in detection[0][0])
        bottom_right = tuple(int(coord) for coord in detection[0][2])
        text = detection[1]
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    st.image(image, caption='Image with Detected Text', use_column_width=True)

    if 'IND' in combined_text:
        st.success("The given number plate is an HSRP number plate")
        normal_register_number = ""
        unique_number = ""
        for text in detected_text:
            if len(text) == 10 and text.isdigit():  
                normal_register_number = text
            elif text.isalnum() and any(char.isdigit() for char in text) and any(char.isalpha() for char in text):
                unique_number = text
        if unique_number:
            st.write("Unique Number:", unique_number)
            values = check_csv_for_number(unique_number, csv_data)
            if values:
                st.write("Details of the given Number plate are as follows : ")
                st.write("reg_no:", values[0])
                st.write("owner:", values[1])
                st.write("Chassis_no:", values[2])
                st.write("ENGINE_N0:", values[3])
                st.write("ADDRESS:", values[4])
               # st.write("PHONE NUMBER:", values[5])
                
            else:
                st.write("No Data found in database.")
        else:
            st.error("Unique number not detected.")
    else:
        st.error("The given number plate is not an HSRP number plate")
        st.text("No Data found in database.")


def main():
    st.markdown(
        "<style>.title-container {  background-image: url('https://i.shgcdn.com/aceda2c7-d994-4107-ba72-8bad9dc5dea9/-/format/auto/-/preview/3000x3000/-/quality/lighter/'); background-size: cover; padding: 180px; }</style>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='title-container'><h1 style='font-style: italic; color: white;'>HSRP NUMBER PLATE RECOGNITION</h1></div>", 
        unsafe_allow_html=True
    )
    pages = {
        "Upload Image": upload_page,
        "Capture via Webcam": webcam_page
    }
    csv_data = read_csv("data.csv")
    selection = st.sidebar.radio("Go to", list(pages.keys()))    
    page = pages[selection]     
    page(csv_data)

if __name__ == "__main__":
    main()

