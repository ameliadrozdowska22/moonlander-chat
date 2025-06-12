import streamlit as st
from utils import generate_response, set_feedback, post_correction, get_deployments
import time
import json
import base64
from typing import Optional
from orq_ai_sdk.models import APIError
from streamlit import _bottom
import base64

KEY = "KasemGPT_Deployment"

def context_section():
    with st.sidebar:
        st.markdown("<p style='font-weight: normal; font-size: 14px;'>Variants</p>", unsafe_allow_html=True)
        
        variable_input = st.selectbox(
            options=["default"] + [i for i in range(1, 11)],
            label="Variants",
            index=0,
            label_visibility="collapsed",
            disabled=False,
        )

    if variable_input:
        st.session_state.context_input_dict["variant"]=variable_input
        
    return


def clear_history(reset_col):
    if reset_col.button("Reset Chat", key="reset_button"):
        st.session_state.messages = []  # Clear the chat history immediately
        st.rerun()  # Force the app to rerun


def add_correction():
    api_token = st.session_state.get("token")
    trace_id = st.session_state.get("trace_id")
    correction_clicked = st.session_state.get("correction_clicked")
    last_message_dict = st.session_state.messages[-1]

    last_message_content = last_message_dict["content"][0]["text"]

    if correction_clicked:
        # Use form to capture user input on Enter or Submit
        with st.form(key=f"correction_form-{st.session_state.correction_widget_key}"):
            user_correction = st.text_area(
                label="Enter your correction",
                value=last_message_content,
                height=None,
                max_chars=None,
                key=f"correction-{st.session_state.correction_widget_key}",
                placeholder="Enter your correction here...",
                label_visibility="collapsed"
            )

            # Submit button inside form
            submitted = st.form_submit_button("Submit Correction")

            if submitted and user_correction:
                post_correction(user_correction, api_token, trace_id)

                # Reset input field after submission
                st.session_state.correction_widget_key += 1

    return

def display_sources(sources):

    with st.expander(label= "Sources", expanded=False, icon="📖"):
                    counter = 0
                    for source in sources:
                        counter += 1
                        file_name = source["file_name"]
                        page_number = source["page_number"]
                        chunk_text = source["chunk"]
                        if page_number == None:
                            st.markdown(f"**{counter}. {file_name}:**")
                        else: 
                            st.markdown(f"**{counter}. {file_name} - page {(int(page_number))}:**")
                        st.markdown(chunk_text) 
    return 


def display_feedback():

    api_token = st.session_state.get("token")
    trace_id = st.session_state.get("trace_id")
    feedback = st.session_state.get("feedback")

    if feedback is not None:
        if int(feedback) == 0:
            set_feedback("bad", api_token, trace_id)

        elif int(feedback) == 1:
            set_feedback("good", api_token, trace_id)

        st.session_state.feedback = None

    return

def manage_chat_history(chat_input):

    # Add the user message to the chat history
    text_message = {
        "role": "user",
        "content": [{"type": "text", "text": chat_input}]
    }
    st.session_state.messages.append(text_message)
    
    # limit the number of past messages given to the model for a reference
    conv_memory = []
    messages = st.session_state.messages

    history_num = 20 # number of maximum past messages given to the model !! CUSTOMIZE IF NEEDED !!
    if history_num < len(messages):
        slicer = len(conv_memory) - history_num
        conv_memory = messages[slicer:]
    else:
        conv_memory = messages

    return conv_memory


def chat_messages_layout(chat_input):

    context = st.session_state.context_input_dict
    token = st.session_state.token

    # display the user text message
    with st.chat_message("user"):
        st.markdown(chat_input)

    # display the response and a source from a model
    with st.chat_message("assistant"):
        try:
            conv_memory = manage_chat_history(chat_input)
            print(context)
            response, sources, trace_id = generate_response(api_token=token, key_input=KEY, conv_memory=conv_memory, context=context)

            st.markdown(response)

            # reset the feedback state
            st.session_state.give_feedback = True
            st.session_state.feedback_widget_key += 1
            st.session_state.feedback = None
            st.session_state.trace_id = trace_id

            # reset the correction state
            st.session_state.give_correction = True
            st.session_state.correction_widget_key += 1

            if sources:
                display_sources(sources)

            # Append the model response in the message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": response}]
            })

        except APIError as e:
            error_dict = json.loads(e.body)
            st.info(error_dict["error"])
            # pass

        except Exception as e:
            print(e)
            # pass

    return


def chat_manager(chat_input):
    """
    Displays the chat history Manages
    """
    token = st.session_state.token

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        # Check if the message content has a type of 'text'
        for content in message["content"]:
                if content["type"] == "text":
                    with st.chat_message(message["role"]):
                        st.markdown(content["text"])

    try:
        # check if the token and key were given to procede with the invoke
        if token and chat_input:
            chat_messages_layout(chat_input)

    except Exception as e:
        print(e)
        # pass

    if st.session_state.give_feedback and st.session_state.give_correction:
        correction_col, feedback_col, empty_col = st.columns([2, 1, 12]) 
        
        # Create pills for adding correction
        correction_clicked = correction_col.pills(
            label="Add correction",
            key=f"correction_button-{st.session_state.correction_widget_key}",
            options="Add correction",
            selection_mode="single",
            default=None,
            label_visibility="collapsed"
        )

        feedback_selected = feedback_col.feedback("thumbs", key=f"feedback-{st.session_state.feedback_widget_key}")

        if feedback_selected is not None: 
            st.session_state.feedback = str(feedback_selected)

        if correction_clicked == "Add correction": 
            st.session_state.correction_clicked = True

    return 


def chat_input_layout():
    """
    Manages the chat input section
    """
    chat_col, reset_col = st._bottom.columns([7, 1])

    chat_input = chat_col.chat_input("Your question")

    clear_history(reset_col)
    
    chat_manager(chat_input)
    
    return


def validate_token(token_input):
    try:
        depl_list = get_deployments(token_input)
    except:
        return False

    if KEY in depl_list:
        return True
    
    return False


def take_token():
    """
    Shows the textfield for the API token.
    Saves the token in the session when given.
    """
    with st.sidebar:

        token_input = st.text_input(
            "Access token",
            label_visibility="visible",
            disabled=False,
            placeholder="Access token")
        
        context_section()

        if token_input:
            if not validate_token(token_input):
                token_input = None
                st.info("Invalid or missing token. Please verify the token and try again.")

        set_button = st.button("Access chat")
            
    if set_button:
        st.session_state["token"] = token_input

    return


def show():
    """
    Initializes the flow of the page.
    """
    take_token()
    token_input =  st.session_state.token

    try:
        if token_input:
            chat_input_layout()

    except:
        pass

    # when the feedback and correction buttons are shown it runs their scripts to react to a change
    if st.session_state.give_feedback and st.session_state.give_correction and st.session_state.messages:
        display_feedback()
        add_correction()