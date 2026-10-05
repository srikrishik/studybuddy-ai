\# StudyBuddy AI



An AI-powered personal study companion designed to help students learn, understand concepts, and generate study material with the help of AI.



StudyBuddy AI uses Google's Gemma model through the Gemini API and provides a simple web interface for interacting with the AI tutor and generating study notes.



\## ✨ Features



\### 🤖 AI Tutor

Ask StudyBuddy questions about programming, technical concepts, or other study topics and receive clear, beginner-friendly explanations.



\### 📚 AI Study Notes

Generate structured study notes for a topic and choose the difficulty level.



\### 📝 Beginner-Friendly Explanations

The AI is designed to explain concepts clearly with examples, headings, bullet points, and code where useful.



\### 💻 Simple Web Interface

A lightweight frontend makes it easy to interact with the AI without requiring a command-line interface.



\### 🔐 Environment-Based API Key

The Gemini API key is stored locally in an environment file and is never included in the source code.



\## 🛠️ Tech Stack



\- Python

\- FastAPI

\- Google GenAI SDK

\- Gemma

\- HTML

\- CSS

\- JavaScript

\- Git \& GitHub



\## 🏗️ Project Structure



```text

studybuddy-ai/

│

├── backend/

│   ├── app/

│   │   ├── services/

│   │   │   ├── ai\_engine.py

│   │   │   └── study\_features.py

│   │   │

│   │   └── main.py

│   │

│   ├── .env

│   └── .venv/

│

├── frontend/

│   └── index.html

│

├── .gitignore

└── README.md

