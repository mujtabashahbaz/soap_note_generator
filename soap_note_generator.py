import streamlit as st
import requests

# List of medical specialties for GPs
specialties = [
    "General Practice",
    "Family Medicine",
    "Internal Medicine",
    "Pediatrics",
    "Geriatrics",
    "Sports Medicine",
    "Preventive Medicine",
    "Emergency Medicine",
    "Occupational Medicine",
]

# Function to get or set the API key
def get_openai_api_key():
    if 'openai_api_key' not in st.session_state or not st.session_state['openai_api_key']:
        st.session_state['openai_api_key'] = st.text_input("Enter your OpenAI API key:", type="password")
    return st.session_state['openai_api_key']

# Specialty-based prompts for SOAP note generation
def get_specialty_prompt(specialty, subjective, objective):
    if specialty == "Pediatrics":
        return f"""You are an experienced pediatrician. Generate a comprehensive SOAP note for a pediatric case.

        Subjective: {subjective}

        Objective: {objective}

        Please provide the following sections:
        1. Assessment:
            - Primary Diagnosis
            - Differential Diagnoses (list at least 3)
        2. Plan:
            - Diagnostic Tests or Procedures
            - Non-Pharmacological Treatments
            - Pharmacological Treatments (specific medication names and dosages if applicable)
            - Patient Education and Counseling
            - Follow-up Recommendations
        """
    
    elif specialty == "Geriatrics":
        return f"""You are an experienced geriatrician. Generate a comprehensive SOAP note for a geriatric case.

        Subjective: {subjective}

        Objective: {objective}

        Please provide the following sections:
        1. Assessment:
            - Primary Diagnosis
            - Differential Diagnoses (list at least 3)
        2. Plan:
            - Diagnostic Tests or Procedures
            - Non-Pharmacological Treatments
            - Pharmacological Treatments (medications with dosages)
            - Patient Education and Counseling
            - Follow-up Recommendations
        """
    
    elif specialty == "Sports Medicine":
        return f"""You are an experienced sports medicine physician. Generate a comprehensive SOAP note for a sports injury or condition.

        Subjective: {subjective}

        Objective: {objective}

        Please provide the following sections:
        1. Assessment:
            - Primary Diagnosis
            - Differential Diagnoses (list at least 3)
        2. Plan:
            - Diagnostic Tests or Procedures (e.g., imaging, physical assessments)
            - Non-Pharmacological Treatments (e.g., physical therapy, exercise)
            - Pharmacological Treatments (medications for pain or inflammation)
            - Patient Education and Counseling
            - Follow-up Recommendations
        """
    
    # Default for General Practice or unspecified specialties
    return f"""You are a general practitioner. Generate a comprehensive SOAP note.

    Subjective: {subjective}

    Objective: {objective}

    Please provide the following sections:
    1. Assessment:
        - Primary Diagnosis
        - Differential Diagnoses (list at least 3)
    2. Plan:
        - Diagnostic Tests or Procedures
        - Non-Pharmacological Treatments
        - Pharmacological Treatments (medications and dosages)
        - Patient Education and Counseling
        - Follow-up Recommendations
    """

# Function to generate SOAP note using OpenAI's REST API
def generate_soap_note(specialty, subjective, objective, api_key):
    prompt = get_specialty_prompt(specialty, subjective, objective)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are an experienced general practitioner generating SOAP notes."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()  # Check for HTTP errors
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit app

# "Back to Homepage" link at the top
st.markdown(
    '<div style="text-align:left;">'
    '<a href="https://aidentify.online" style="font-size:24px; color:white; text-decoration:none;">'
    '⬅️ Back to Homepage</a></div>', 
    unsafe_allow_html=True
)

st.title('AI-Powered SOAP Note Generator for General Practitioners')

# API Key input
api_key = get_openai_api_key()

# Select the medical specialty
specialty = st.selectbox("Select Your Medical Specialty:", specialties)

# Subjective and Objective inputs (manual entry)
st.subheader('Subjective')
subjective = st.text_area("Subjective information:", height=100)

st.subheader('Objective')
objective = st.text_area("Objective information:", height=100)

# Generate button
if st.button('Generate SOAP Note'):
    if subjective and objective:
        if api_key:
            with st.spinner(f'Generating SOAP Note for {specialty}...'):
                soap_note = generate_soap_note(specialty, subjective, objective, api_key)

            # Display the SOAP note as is (since it's already in the correct format)
            st.markdown(soap_note)
        else:
            st.warning('Please enter your OpenAI API key to generate the SOAP note.')
    else:
        st.warning('Please provide both subjective and objective information.')

# "Back to Homepage" link at the bottom
st.markdown(
    '<div style="text-align:left;">'
    '<a href="https://aidentify.online" style="font-size:24px; color:white; text-decoration:none;">'
    '⬅️ Back to Homepage</a></div>', 
    unsafe_allow_html=True
)

# Add information about the app
st.sidebar.title('About')
st.sidebar.info('This app generates comprehensive SOAP notes tailored to various medical subspecialties. Choose your specialty, input subjective and objective details, and let AI help generate the rest of the note.')

# Add a note about the API key
st.sidebar.title('API Key')
st.sidebar.info('This app requires an OpenAI API key to function. Your API key is not stored permanently and must be re-entered each time you restart the app.')

# Add a disclaimer
st.sidebar.title('Disclaimer')
st.sidebar.warning('This app is for educational and demonstration purposes only. The generated SOAP notes should not be used for actual medical decision-making without review by a licensed healthcare professional.')
