# First Step — AI Chatbot

An AI-powered chatbot built using Python, Streamlit and OpenRouter API.

**First Step** started as a personal project to understand how AI chatbots work and how to integrate AI models into a real-world application. It gradually evolved into a web-based chatbot that can handle text conversations, read documents and understand images.

> Your 1st step towards smarter conversations.

## Live Demo

[Try First Step](ADD_YOUR_STREAMLIT_APP_LINK_HERE)

## Features

- **AI Conversations:** Chat with AI using OpenRouter models.
- **Document Understanding:** Upload PDF, DOCX and TXT files and ask questions about their contents.
- **Image Understanding:** Upload JPG, JPEG, PNG and WEBP images for analysis.
- **Handwritten Notes Recognition:** Extract and understand text from images of handwritten notes.
- **Custom Interface:** A simple, dark-themed interface built with Streamlit.
- **Cloud Deployment:** Hosted using Streamlit Community Cloud.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application and user interface |
| OpenRouter API | AI model integration |
| OpenAI Python SDK | API communication |
| python-dotenv | Local environment variable management |
| pypdf | PDF text extraction |
| python-docx | DOCX text extraction |
| Git & GitHub | Version control and project hosting |
| Streamlit Community Cloud | Application deployment |

## How I Built It

### 1. Setting Up the Development Environment
- Installed Python and Visual Studio Code.
- Created a dedicated project folder.
- Set up a Python virtual environment.
- Installed the required Python libraries.

### 2. Building the Initial Chatbot
- Created the main Python file (`first_step.py`).
- Used Streamlit to build the chatbot interface.
- Added a chat input and message display system.
- Implemented conversation handling using Streamlit session state.

### 3. Integrating the AI Model
- Created an API key through OpenRouter.
- Integrated the OpenRouter API using the OpenAI Python SDK.
- Configured the chatbot to send messages to the selected AI model.
- Added temperature control for response creativity.

### 4. Improving the User Interface
- Designed a dark-themed interface.
- Added First Step branding.
- Created sidebar controls for model selection and conversation management.
- Improved the overall chat experience.

### 5. Adding Document Understanding
- Added file upload functionality for PDF, DOCX and TXT files.
- Used `pypdf` and `python-docx` to extract document text.
- Implemented basic keyword-based retrieval to find relevant document sections.
- Passed relevant sections to the AI model to answer user questions.

### 6. Adding Image Understanding
- Added image upload support.
- Converted uploaded images into Base64 data URLs.
- Integrated a vision-capable AI model through OpenRouter.
- Enabled image analysis and handwritten notes recognition.

### 7. Securing API Credentials
- Used environment variables for local development.
- Used Streamlit Secrets for cloud deployment.
- Kept API credentials out of the GitHub repository using `.gitignore`.

### 8. Deploying the Application
- Created a GitHub repository.
- Uploaded the project using Git.
- Connected the repository to Streamlit Community Cloud.
- Configured API credentials in Streamlit Cloud Secrets.
- Deployed the application and tested its features online.

## Installation and Local Setup

### Prerequisites
- Python
- Git
- An OpenRouter API key

### Step 1: Clone the repository

```bash
git clone https://github.com/dipangshu-core/First-Step.git
```

### Step 2: Open the project folder

```bash
cd First-Step
```

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

### Step 4: Activate the virtual environment

**Windows:**

```powershell
.venv\Scripts\activate
```

### Step 5: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure your API key

Create a `.env` file in the project folder:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Never upload your actual API key to GitHub.

### Step 7: Run the application

```bash
streamlit run first_step.py
```

The application should open in your browser.

## Project Structure

```text
First-Step/
│
├── first_step.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env
```

*Note: `.env` is a local configuration file and should not be committed to GitHub.*

## Current Limitations

- Document retrieval currently uses basic keyword matching rather than a vector database.
- Scanned PDFs may require OCR to extract text.
- Image analysis depends on the selected vision model.
- AI responses and availability depend on the selected OpenRouter model and its usage limits.

## Future Improvements

- Persistent chat history.
- Better conversation memory.
- Improved document retrieval using embeddings.
- OCR support for scanned documents.
- More AI model options.
- Improved chat management and user experience.

## Author

**Dipangshu Poddar**

BCA — Data Science & Cybersecurity

Built as a personal learning project to explore Python, AI integration and application development.

---

*First Step is an ongoing project. More features and improvements are planned.*
# First Step — AI Chatbot

> Your 1st step towards smarter conversations.

🚀 **[Try First Step — Live Demo](https://first-step-bpfqu2yqdtkaqx9smsve3d.streamlit.app/)**

An AI-powered chatbot built using Python, Streamlit and OpenRouter API.
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://first-step-bpfqu2yqdtkaqx9smsve3d.streamlit.app/)
