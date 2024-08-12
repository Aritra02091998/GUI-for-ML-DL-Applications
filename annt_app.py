import streamlit as st
import pandas as pd
from PIL import Image

version_num = 2.0

# Set the viewport to wide (100% page width)
st.set_page_config(layout="wide")

# Load the data from CSV
data = pd.read_csv("./ad_annt.csv")

# Store all possible indices from the CSV in a set
valid_indices = set(data["index"])

# Load the saved responses from the file
response_file = "./user_responses.csv"
try:
    saved_responses = pd.read_csv(response_file)
    filled_indices = set(saved_responses["index"])
except FileNotFoundError:
    saved_responses = pd.DataFrame(columns=["index", "is_it_relevant", "more_helpful_than_gt", "is_it_noisy"])
    filled_indices = set()

# Initialize session state to keep track of the current index and saved indices
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "saved_indices" not in st.session_state:
    st.session_state.saved_indices = filled_indices

# Function to display the current data entry
def display_entry(index):
    entry = data.iloc[index]
    
    # Create two columns, one for the image and one for the text
    col1, col2 = st.columns(2)

    # Display image on the left in col1
    with col1:
        st.text(f"Annotation App_v{version_num}")

        image = Image.open(entry["image_path"])
        image = image.resize((550, 310))  # Resize to 550x310 pixels

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

# Function to save the current response to the file
def save_response():
    response = {
        "index": data.iloc[st.session_state.current_index]["index"],
        "is_it_relevant": st.session_state.is_it_relevant,
        "more_helpful_than_gt": st.session_state.more_helpful_than_gt,
        "is_it_noisy": st.session_state.is_it_noisy
    }
    
    # Append the response to the DataFrame and save it to the CSV file
    global saved_responses
    saved_responses.loc[len(saved_responses)] = response
    saved_responses.to_csv(response_file, index=False)
    st.session_state.saved_indices.add(response["index"])

# Display the current entry
display_entry(st.session_state.current_index)

# Lower portion for user inputs
st.write("### Annotation")

# Check if the current entry is in the saved responses and disable fields if so
current_entry_index = data.iloc[st.session_state.current_index]["index"]
saved_entry = saved_responses[saved_responses["index"] == current_entry_index]

is_editable = st.session_state.current_index not in st.session_state.saved_indices

if not is_editable or not saved_entry.empty:
    is_editable = False
    if not saved_entry.empty:
        st.session_state.is_it_relevant = saved_entry["is_it_relevant"].values[0]
        st.session_state.more_helpful_than_gt = saved_entry["more_helpful_than_gt"].values[0]
        st.session_state.is_it_noisy = saved_entry["is_it_noisy"].values[0]

# Define the selectbox with disabled state handling
st.selectbox("Is the Generated Explanation Relevant?", ["Yes", "No"], key="is_it_relevant", disabled=not is_editable, placeholder="Select contact method...")
st.selectbox("Is it more helpful than the Ground Truth explanation?", ["Yes", "No"], key="more_helpful_than_gt", disabled=not is_editable, placeholder="Select contact method...")
st.selectbox("Is it noisy?", ["Yes", "No"], key="is_it_noisy", disabled=not is_editable, placeholder="Select contact method...")

# Function to validate the user input
def validate_input():
    # Fields are validated only if they are editable (i.e., the entry is not already saved)
    if is_editable and (st.session_state.is_it_relevant == "SELECT" or st.session_state.more_helpful_than_gt == "SELECT" or st.session_state.is_it_noisy == "SELECT"):
        return False
    return True

# Function to calculate and display the remaining entries
def display_remaining_entries():
    remaining_indices = valid_indices - st.session_state.saved_indices
    remaining_count = len(remaining_indices)
    st.write(f"**Remaining Entries to Fill: {remaining_count}**")

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Previous"):
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.rerun()

with col2:
    if st.button("Next"):
        if st.session_state.current_index < len(data) - 1:
            if validate_input():
                if is_editable:
                    save_response()
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.warning("Please make a selection for all fields before saving or proceeding to the next entry.")
        else:
            st.warning("End of data reached.")

with col3:
    if st.button("Save"):
        if validate_input():
            save_response()
            st.success("Response saved!")
            st.rerun()
        else:
            st.warning("Please make a selection for all fields before saving.")

# Display the remaining entries after each "Next" button click
display_remaining_entries()

# "Go to Index" functionality
st.write("### Go to a Specific Index")
go_index = st.text_input("Enter the index:", "")
if st.button("Go"):
    try:
        go_index = int(go_index)
        if go_index in valid_indices:
            target_index = data.index[data["index"] == go_index].tolist()[0]
            st.session_state.current_index = target_index
            st.rerun()
        else:
            st.warning(f"Index {go_index} is not a valid index. Please enter a valid index from the dataset.")
    except ValueError:
        st.warning("Please enter a valid integer index.")
