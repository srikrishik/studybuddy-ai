# StudyBuddy AI

An AI-powered personal study companion designed to help students learn,
understand concepts, study from their own documents, and practice with
AI-generated quizzes and flashcards.

StudyBuddy AI uses Google's Gemma model through the Gemini API and provides
a simple web interface for interacting with an AI tutor and generating
personalized study material.

## ✨ Features

### 🤖 AI Tutor

Ask StudyBuddy questions about programming, technical concepts, or other
study topics and receive clear, beginner-friendly explanations.

### 📚 AI Study Notes

Generate structured study notes for a topic and choose the difficulty level.

### 📄 PDF-Based Learning

Upload study documents and process their content for AI-assisted learning.

### 🔎 Document Retrieval / RAG

StudyBuddy can retrieve relevant content from uploaded documents so that
AI responses can be grounded in the student's study material.

### 📝 AI Quiz Generation

Generate multiple-choice quizzes using Gemma.

Features include:

- Topic and difficulty selection
- AI-generated questions
- Correct answers
- Explanations
- Quiz submission and scoring
- Quiz attempt history

### 🎴 AI Flashcard Generation

Generate question-and-answer flashcards for quick revision.

Features include:

- Topic-based flashcard generation
- Difficulty support
- Frontend flashcard interface
- Persistent flashcard sets
- Mark cards for revision

### 📊 Progress Dashboard

Track learning activity through:

- Total quiz attempts
- Average score
- Latest quiz score
- Topic-level progress
- Topics needing more practice
- Recent quiz attempts

### 💾 MongoDB Persistence

StudyBuddy stores important learning data in MongoDB so that quiz attempts,
flashcards, document metadata, and progress remain available after refreshing
or restarting the application.

### 🔐 Environment-Based API Keys

API keys and database credentials are stored in environment variables and
are never included in the source code.

## 🛠️ Tech Stack

- Python
- FastAPI
- Google GenAI SDK
- Gemma
- MongoDB Atlas
- PyMongo
- PDF processing with pypdf
- HTML
- CSS
- JavaScript
- Git & GitHub
- Render

## 📁 Project Structure

```text
studybuddy-ai/
│
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── ai_engine.py
│   │   │   ├── chunk_service.py
│   │   │   ├── database.py
│   │   │   ├── document_repository.py
│   │   │   ├── flashcard_repository.py
│   │   │   ├── flashcard_service.py
│   │   │   ├── mongodb.py
│   │   │   ├── pdf_service.py
│   │   │   ├── progress_repository.py
│   │   │   ├── quiz_repository.py
│   │   │   ├── quiz_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── retrieval_service.py
│   │   │   └── study_features.py
│   │   │
│   │   ├── __init__.py
│   │   └── main.py
│   │
│   ├── gemini_test.py
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md