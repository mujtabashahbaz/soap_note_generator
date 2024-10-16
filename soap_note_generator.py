import streamlit as st
import re
import requests

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

# Function to generate SOAP note using OpenAI's REST API
def generate_soap_note(subjective, objective, api_key):
    prompt = f"""Generate a comprehensive medical SOAP note based on the following information:

Subjective: {subjective}

Objective: {objective}

Please provide the following sections:
1. Assessment:
   - Primary diagnosis
   - Differential diagnoses (list at least 3)
2. Plan:
   - Diagnostic tests or procedures
   - Treatments:
     a) Non-pharmacological interventions
     b) Pharmacological interventions (include specific prescriptions with dosage and frequency)
   - Patient education and counseling
   - Follow-up recommendations

Ensure the note is detailed, professional, and follows standard medical terminology and format."""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an experienced physician generating comprehensive SOAP notes, including differential diagnoses and detailed treatment plans with medications and dosages."},
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

# Function to transcribe audio to text using OpenAI's Whisper API via REST
def transcribe_audio(file, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    files = {
        'file': file,
        'model': (None, 'whisper-1')
    }

    try:
        response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files)
        response.raise_for_status()  # Check for HTTP errors
        result = response.json()
        return result['text']
    except Exception as e:
        return f"Error: {str(e)}"

# Function to parse transcribed text and classify information into Subjective and Objective
def classify_subjective_objective(transcription, api_key):
    prompt = f"""You will classify the provided text into Subjective (patient-reported symptoms) and Objective (doctor's examination findings).
    
Text: {transcription}

Classify it into the following format:
Subjective: [patient's reported symptoms]
Objective: [doctor's examination findings]
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a physician assistant helping to classify subjective and objective information."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()  # Check for HTTP errors
        result = response.json()
        return extract_info(result['choices'][0]['message']['content'])
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert SOAP note into styled HTML
def convert_to_html(soap_note):
    # Split the SOAP note into Subjective and Objective parts if possible
    if 'Objective:' in soap_note:
        parts = soap_note.split('Objective:')
        subjective = parts[0].strip()  # The part before 'Objective:'
        objective = parts[1].strip()   # The part after 'Objective:'
    else:
        # If 'Objective:' is not found, treat everything as subjective and leave objective blank
        subjective = soap_note.strip()
        objective = "Objective information not found."

    # Example of styling for SOAP note
    styled_html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 10px; border: 1px solid #ccc; background-color: #f9f9f9;">
        <h2 style="color: #2c3e50;">SOAP Note</h2>
        <p><strong>Subjective:</strong> {subjective}</p>
        <p><strong>Objective:</strong> {objective}</p>
    </div>
    """
    return styled_html

# JavaScript to add the copy-to-clipboard functionality
def get_copy_button_html(styled_html):
    # Escape backticks and ensure the HTML is correctly formatted for JavaScript
    escaped_html = styled_html.replace("`", "\\`").replace("\n", "\\n").replace('"', '\\"')
    
    return f"""
    <button onclick="copyToClipboard()">Copy SOAP Note</button>
    <script>
        function copyToClipboard() {{
            const text = `{escaped_html}`;
            const el = document.createElement('textarea');
            el.value = text;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            alert('SOAP Note copied to clipboard!');
        }}
    </script>
    """

# Streamlit app
st.title('Enhanced AI SOAP Note Generator with Speech-to-Text')

# API Key input
api_key = get_openai_api_key()

# Audio file upload for transcription
st.subheader('Upload an Audio File (Optional)')
audio_file = st.file_uploader("Upload an audio file for transcription (e.g., a patient conversation)", type=['wav', 'mp3', 'm4a'])

# Transcribe button
if st.button('Transcribe Audio'):
    if audio_file and api_key:
        with st.spinner('Transcribing audio...'):
            transcription = transcribe_audio(audio_file, api_key)
            if transcription.startswith("Error"):
                st.error(transcription)
            else:
                with st.spinner('Classifying Subjective and Objective...'):
                    subjective, objective = classify_subjective_objective(transcription, api_key)
                    if subjective and objective:
                        st.session_state['subjective'] = subjective
                        st.session_state['objective'] = objective
                        st.success('Subjective and Objective extracted successfully!')
                    else:
                        st.error('Error in extracting Subjective and Objective.')
    else:
        st.warning('Please upload an audio file and provide a valid API key.')

# Subjective and Objective inputs (manual entry)
st.subheader('Subjective')
subjective = st.text_area("Subjective information:", value=st.session_state.get('subjective', ''), height=100)

st.subheader('Objective')
objective = st.text_area("Objective information:", value=st.session_state.get('objective', ''), height=100)

# Generate button
if st.button('Generate Enhanced SOAP Note'):
    if subjective and objective:
        if api_key:
            with st.spinner('Generating Enhanced SOAP Note...'):
                soap_note = generate_soap_note(subjective, objective, api_key)

            # Convert SOAP note to styled HTML
            styled_html = convert_to_html(soap_note)

            # Display the SOAP note as styled HTML
            st.markdown(styled_html, unsafe_allow_html=True)

            # Add the copy button
            copy_button_html = get_copy_button_html(styled_html)
            st.markdown(copy_button_html, unsafe_allow_html=True)
        else:
            st.warning('Please enter your OpenAI API key to generate the SOAP note.')
    else:
        st.warning('Please provide both subjective and objective information.')

# Add information about the app
st.sidebar.title('About')
st.sidebar.info('This enhanced app uses AI to generate comprehensive medical SOAP notes, including differential diagnoses and detailed treatment plans with prescriptions. You can upload an audio file for automatic transcription or manually input subjective and objective information.')

# Add a note about the API key
st.sidebar.title('API Key')
st.sidebar.info('This app requires an OpenAI API key to function. You\'ll be prompted to enter it when you start the app. Your API key is not stored permanently and will need to be re-entered each time you restart the app.')
