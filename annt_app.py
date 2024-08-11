import streamlit as st
import pandas as pd
from PIL import Image

version_num = 1.0

# Set the viewport to wide (100% page width)
st.set_page_config(layout="wide")

# Load the data from CSV
data = pd.read_csv("ad_annt.csv")

# Initialize session state to keep track of the current index and user responses
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "responses" not in st.session_state:
    st.session_state.responses = []

# Function to display the current data entry
def display_entry(index):
    entry = data.iloc[index]
    
    # Create two columns, one for the image and one for the text
    col1, col2 = st.columns(2)

    # Display image on the left in col1
    with col1:
        st.text(f"Annotation App_v{version_num}")

        image = Image.open(entry["image_path"])
        image = image.resize((550, 310))  # Resize to 250x250 pixels

        st.image(image)
        st.subheader("Question", divider=True)
        st.markdown(f"{entry['question']} ?")
        st.subheader("Answer", divider=True)
        st.text(f"{entry['answer']}")
    
    # Display text information on the right in col2
    with col2:
        st.text(f"Index: {entry['index']}")
        st.subheader("Ground Truth Explanation:", divider=True)
        st.markdown(f"{entry['gt_explanation']}")
        st.subheader("Generated Explanation:", divider=True)
        st.markdown(f"{entry['gen_explanation']}")

        st.subheader("Retrieved Facts:", divider=True)
        for i in range(0, 5):
            st.markdown(f"{i+1}. {entry[f'ret{i}']}")

# Function to save the current response
def save_response():
    response = {
        "index": data.iloc[st.session_state.current_index]["index"],
        "is_it_relevant": st.session_state.is_it_relevant,
        "more_helpful_than_gt": st.session_state.more_helpful_than_gt,
        "is_it_noisy": st.session_state.is_it_noisy
    }
    st.session_state.responses.append(response)

# Display the current entry
display_entry(st.session_state.current_index)

# Lower portion for user inputs
st.write("### Annotation")
st.selectbox("Is the Generated Explanation Relevant ?", ["","Yes", "No"], key="is_it_relevant")
st.selectbox("Is it more helpful than the Ground Truth explanation ?", ["","Yes", "No"], key="more_helpful_than_gt")
st.selectbox("Is it noisy ?", ["","Yes", "No"], key="is_it_noisy")

# Navigation buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Previous"):
        if st.session_state.current_index > 0:
            save_response()
            st.session_state.current_index -= 1
            st.rerun()

with col2:
    if st.button("Next"):
        if st.session_state.current_index < len(data) - 1:
            save_response()
            st.session_state.current_index += 1
            st.rerun()
        else:
            st.warning("End of data reached.")

with col3:
    if st.button("Save"):
        save_response()
        st.success("Response saved!")

with col4:
    if st.button("Flush to File"):
        pd.DataFrame(st.session_state.responses).to_csv("user_responses.csv", index=False)
        st.session_state.responses = []
        st.success("Responses flushed to file!")
