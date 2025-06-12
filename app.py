import streamlit as st
from subpages import generalDemo

APP_TITLE = 'Orq.ai Chat'
st.set_page_config(APP_TITLE, page_icon="📈", layout="wide")

st.sidebar.image("assets/orq_logo.png", width=110)

# Initialize session state variables
if "messages" not in st.session_state: # Initialize chat history
    st.session_state.messages = []
if "token" not in st.session_state:
    st.session_state.token = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Main"
if "feedback" not in st.session_state: # Initialize the feedback value
    st.session_state.feedback = None
if "give_feedback" not in st.session_state: # Initialize the feedback state (shown/ not shown)
   st.session_state.give_feedback = False
if "feedback_widget_key" not in st.session_state: # Dynamically update the feedback widget's key for resetting
    st.session_state.feedback_widget_key = 0
if "trace_id" not in st.session_state:
    st.session_state.trace_id = 0
if "give_correction" not in st.session_state: # Initialize the correction state (shown/ not shown)
   st.session_state.give_correction = False
if "correction_widget_key" not in st.session_state: # Dynamically update the correction widget's key for resetting
    st.session_state.correction_widget_key = 0
if "correction" not in st.session_state: # Initialize the correction value
    st.session_state.correction_clicked = False
if "context_input_dict" not in st.session_state: # Initialize context dictionary
    st.session_state.context_input_dict = {"variant": "default"}



def navigate_to(page):
    if st.session_state.current_page != page:
        st.session_state.messages = []
        
    st.session_state.current_page = page

def style():
    """
    This function sets the customized CSS styles of a title, regular expander and side-menu-expander.

    Param: None
    Return: None
    """

    st.markdown(
    """
    <style>
        h1 {
            margin-bottom: 0px;
        }

        /* Expander style in the main content */
        div[data-testid="stExpander"] details summary p {
            font-size: 1rem;
            font-weight: 400;
        }
        /* Expander style in the sidebar */
        section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary p {
            font-size: 1.3rem;
            font-weight: 600;
        }
        </style>
    """,
    unsafe_allow_html=True
    )

    return

# Main page content
st.title(APP_TITLE)
style()
generalDemo.show()
