import streamlit as st
import requests

# List of dental specialties
specialties = [
    "General Dentistry",
    "Orthodontics",
    "Periodontics",
    "Endodontics",
    "Prosthodontics",
    "Pediatric Dentistry",
    "Oral and Maxillofacial Surgery",
    "Oral and Maxillofacial Pathology",
    "Oral and Maxillofacial Radiology",
    "Dental Public Health",
    "Oral Medicine"
]

# Function to get or set the API key
def get_openai_api_key():
    if 'openai_api_key' not in st.session_state or not st.session_state['openai_api_key']:
        st.session_state['openai_api_key'] = st.text_input("Enter your OpenAI API key:", type="password")
    return st.session_state['openai_api_key']

# Specialty-based prompts for SOAP note generation
def get_specialty_prompt(specialty, subjective, objective):
    if specialty == "Orthodontics":
        return f"""You are an experienced orthodontist. Generate a comprehensive SOAP note for the following case:

        Subjective: {subjective}

        Objective: {objective}

        Please provide the following sections:
        1. Assessment:
            - Primary Diagnosis
            - Differential Diagnoses (list at least 3)
        2. Plan:
            - Diagnostic Tests or Procedures
            - Non-Pharmacological Treatments (e.g., braces, aligners)
            - Pharmacological Treatments (with specific medication names and dosages if needed)
            - Patient Education and Counseling
            - Follow-up Recommendations
        """
    
    elif specialty == "Periodontics":
        return f"""You are an experienced periodontist. Generate a comprehensive SOAP note for a periodontal case.

        Subjective: {subjective}

        Objective: {objective}

        Please provide the following sections:
        1. Assessment:
            - Primary Diagnosis of any periodontal disease
            - Differential Diagnoses (list at least 3)
        2. Plan:
            - Diagnostic Tests or Procedures
            - Non-Pharmacological Treatments (e.g., scaling, root planing)
            - Pharmacological Treatments (with medication names and dosages, e.g., antibiotics)
            - Patient Education and Counseling
            - Follow-up Recommendations
        """
    
    elif specialty == "Endodontics":
        return f"""You are an experienced endodontist. Generate a SOAP note for an endodontic case.

        Subjective: {subjective}

        Objective: {objective}

        Please provide the following sections:
        1. Assessment:
            - Primary Diagnosis related to dental pulp issues
            - Differential Diagnoses (list at least 3)
        2. Plan:
            - Diagnostic Tests or Procedures (e.g., X-rays)
            - Non-Pharmacological Treatments (e.g., root canal treatment)
            - Pharmacological Treatments (medications with dosages for pain or infection management)
            - Patient Education and Counseling
            - Follow-up Recommendations
        """
    
    # Add similar prompts for other specialties...

    # Default for General Dentistry or unspecified specialties
    return f"""You are a general dentist. Generate a comprehensive SOAP note.

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
            {"role": "system", "content": "You are an experienced dentist generating SOAP notes."},
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
st.title('AI-Powered SOAP Note Generator for Dentists')

# API Key input
api_key = get_openai_api_key()

# Select the dental specialty
specialty = st.selectbox("Select Your Dental Specialty:", specialties)

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

# Add information about the app
st.sidebar.title('About')
st.sidebar.info('This app generates comprehensive medical SOAP notes tailored to various dental subspecialties. Choose your specialty, input subjective and objective details, and let AI help generate the rest of the note.')

# Add a note about the API key
st.sidebar.title('API Key')
st.sidebar.info('This app requires an OpenAI API key to function. Your API key is not stored permanently and must be re-entered each time you restart the app.')

# Add a disclaimer
st.sidebar.title('Disclaimer')
st.sidebar.warning('This app is for educational and demonstration purposes only. The generated SOAP notes should not be used for actual medical decision-making without review by a licensed healthcare professional.')
