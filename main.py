import requests
import google.generativeai as genai
import time
import streamlit as st
import random

# Set custom theme and layout
st.set_page_config(
    page_title="GemiLla",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Streamlit session state for conversation history
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# API LLAMA-3 from Meta
LLAMA_API_KEY = "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"
def call_llama_api(prompt, api_key):
    LLAMA_BASE_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"temperature": 0.7, "max_tokens": 100}}

    response = requests.post(LLAMA_BASE_URL, headers=headers, json=payload)
    if response:
        return response.json()[0]["generated_text"]
    else:
        return "Failed to get response from LLaMA."


# API Gemini from Google
GEMINI_API_KEY = "AIzaSyCIZZR1auG4KI15hh8Ah2w-25hTphRvNwk"
def call_gemini_api(prompt, api_key):
    genai.configure(api_key=api_key)
    # Set up the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    convo = model.start_chat(history=[])
    convo.send_message(prompt)
    return convo.last.text
    
# Streamlit UI
st.title("GemiLla: Conversational Agents")

# Topic selection with customized prompts
topic_options = {
    "Artificial Intelligence": "How do you see AI shaping the future?",
    "Technology": "What's the latest tech that excites you?",
    "Health": "What are some healthy habits you recommend?",
    "Sports": "What's your favorite sport and why?",
    "Entertainment": "What's the best movie you've seen recently?",
    "Travel": "Where's the best place you've traveled to?",
    "Education": "What do you think about modern education?",
    "Food": "What's your favorite cuisine?",
}
selected_topic = st.selectbox("Choose a topic:", list(topic_options.keys()))
rounds = st.number_input("Select the number of rounds:", min_value=1, max_value=10, value=2)
custom_prompt = st.text_input("Add your custom prompt (optional):", "")

gemini_icon = "✨"
llama_icon = "🦙" 

# Combine Gemini responses into a single list
gemini_responses = [
    f"It's great to be here! What do you have in mind about {topic_options[selected_topic]}?",
    f"I'm excited to discuss {topic_options[selected_topic]}! Tell me more!",
    f"I'm ready to explore! What should we talk about {topic_options[selected_topic]}?",
    f"I'm curious about your thoughts. What's on your mind about {topic_options[selected_topic]}?",
]
    
if st.button("Start Conversation"):
    # Initial prompt with topic and custom message
    if custom_prompt:
        initial_prompt = f"Hello, Gemini and LLaMA, Let's talk about {topic_options[selected_topic]} and {custom_prompt}"
    else:
        initial_prompt = f"Hello, Gemini and LLaMA, Let's talk about {topic_options[selected_topic]}"
    
    # Randomly select a response to add variety
    gemini_response =   random.choice(gemini_responses)
    
    st.markdown(f"{gemini_icon} <span style='color:yellow'>Gemini:</span> {gemini_response}", unsafe_allow_html=True)
    st.session_state["conversation_history"].append({"agent": "Gemini", "icon": gemini_icon, "response": gemini_response})

    for i in range(rounds):
        if i == rounds - 1:
            st.markdown(f"<span style='color:red'>Final round</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:green'>Round {i + 1}</span>", unsafe_allow_html=True)

        # LLaMA Response
        llama_response = call_llama_api(gemini_response, LLAMA_API_KEY)
        llama_personality = "Greetings! I'm always up for a good discussion." + " " + llama_response
        st.markdown(f"{llama_icon} <span style='color:yellow'>LLaMA:</span> {llama_personality}", unsafe_allow_html=True)
        st.session_state["conversation_history"].append({"agent": "LLaMA", "icon": llama_icon, "response": llama_personality})
        time.sleep(10)
        
        gemini_response = call_gemini_api(llama_response, GEMINI_API_KEY)
        gemini_personality ="Woow, great insights," + " " + gemini_response
        st.markdown(f"{gemini_icon} <span style='color:yellow'>Gemini:</span> {gemini_response}", unsafe_allow_html=True)
        st.session_state["conversation_history"].append({"agent": "Gemini", "icon": gemini_icon, "response": gemini_response})
        time.sleep(10)
        
    # Give a goodbye message with unique elements
    gemini_farewell = random.choice([
        "It was a pleasure chatting with you! Have an awesome day!",
        "Thanks for the great conversation! See you next time!",
        "It's been fun! Let's talk again soon!",
    ])
    llama_farewell = random.choice([
        "Thanks for the chat! I look forward to our next one.",
        "It was wonderful talking with you! Take care!",
        "I'm already looking forward to our next conversation!",
    ])
    
    st.markdown(f"{gemini_icon} <span style='color:yellow'>Gemini:</span> {gemini_farewell}", unsafe_allow_html=True)
    st.markdown(f"{llama_icon} <span style='color:yellow'>LLaMA:</span> {llama_farewell}", unsafe_allow_html=True)
    st.session_state["conversation_history"].append({"agent": "Gemini", "icon": gemini_icon, "response": gemini_farewell})
    st.session_state["conversation_history"].append({"agent": "LLaMA", "icon": llama_icon, "response": llama_farewell})

# Display the conversation history from session state
st.header("Conversation History")
for entry in st.session_state["conversation_history"]:
    st.markdown(f"{entry['icon']} <span style='color:yellow'>{entry['agent']}:</span> {entry['response']}", unsafe_allow_html=True)