import streamlit as st
import re

# Check if openai is installed
try:
    from openai import OpenAI
    openai_installed = True
except ImportError:
    openai_installed = False

# Function to get or set the API key
def get_openai_api_key():
    if 'openai_api_key' not in st.session_state or not st.session_state['openai_api_key']:
        st.session_state['openai_api_key'] = st.text_input("Enter your OpenAI API key:", type="password")
    return st.session_state['openai_api_key']

def extract_info(conversation):
    # Extract Subjective information
    subjective_match = re.search(r'Subjective:(.*?)(?:Objective:|$)', conversation, re.DOTALL | re.IGNORECASE)
    subjective = subjective_match.group(1).strip() if subjective_match else ""
    
    # Extract Objective information
    objective_match = re.search(r'Objective:(.*?)(?:Assessment:|$)', conversation, re.DOTALL | re.IGNORECASE)
    objective = objective_match.group(1).strip() if objective_match else ""
    
    return subjective, objective

def generate_soap_note(subjective, objective):
    if not openai_installed:
        return "Error: OpenAI library is not installed. Please install it to use this feature."

    api_key = get_openai_api_key()
    if not api_key:
        return "Error: Please enter a valid OpenAI API key to use this feature."

    client = OpenAI(api_key=api_key)
    prompt = f"Generate a medical SOAP note based on the following information:\n\nSubjective: {subjective}\n\nObjective: {objective}\n\nPlease provide the Assessment and Plan sections."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates medical SOAP notes."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app
st.title('AI SOAP Note Generator')

if not openai_installed:
    st.warning("The OpenAI library is not installed. Some features of this app may not work.")
    st.info("To install the OpenAI library, run the following command in your terminal:")
    st.code("pip install openai")
    st.info("After installing, please restart the Streamlit app.")

# API Key input
api_key = get_openai_api_key()

# ChatGPT conversation input
st.subheader('ChatGPT Conversation')
conversation = st.text_area("Paste your ChatGPT conversation here:", height=200)

# Extract button
if st.button('Extract Subjective and Objective'):
    if conversation:
        subjective, objective = extract_info(conversation)
        st.session_state['subjective'] = subjective
        st.session_state['objective'] = objective
    else:
        st.warning('Please paste a conversation before extracting.')

# Subjective and Objective inputs
st.subheader('Subjective')
subjective = st.text_area("Subjective information:", value=st.session_state.get('subjective', ''), height=100)

st.subheader('Objective')
objective = st.text_area("Objective information:", value=st.session_state.get('objective', ''), height=100)

# Generate button
if st.button('Generate SOAP Note'):
    if subjective and objective:
        if api_key:
            with st.spinner('Generating SOAP Note...'):
                soap_note = generate_soap_note(subjective, objective)
            st.subheader('Generated SOAP Note')
            st.text_area("", value=soap_note, height=300)
        else:
            st.warning('Please enter your OpenAI API key to generate the SOAP note.')
    else:
        st.warning('Please provide both subjective and objective information.')

# Add information about the app
st.sidebar.title('About')
st.sidebar.info('This app uses AI to generate medical SOAP notes based on subjective and objective information. You can paste a ChatGPT conversation to automatically extract this information, or input it manually.')

# Add a note about the API key
st.sidebar.title('API Key')
st.sidebar.info('This app requires an OpenAI API key to function. You\'ll be prompted to enter it when you start the app. Your API key is not stored permanently and will need to be re-entered each time you restart the app.')