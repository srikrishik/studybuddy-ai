from uuid import uuid4







from fastapi import FastAPI, HTTPException, UploadFile, File



from fastapi.middleware.cors import CORSMiddleware



from pydantic import BaseModel, Field







from app.services.ai_engine import (



    get_ai_response,



    AIProviderError,



    AIProviderTimeoutError,



)







from app.services.database import (



    initialize_database,



    save_quiz_attempt,



    get_quiz_attempts,



)







from app.services.pdf_service import extract_pdf_text



from app.services.chunk_service import chunk_pages



from app.services.rag_service import answer_from_document



from app.services.quiz_service import generate_quiz
from app.services.flashcard_service import generate_flashcards











app = FastAPI(



    title="StudyBuddy AI",



    description="Your Personal Open-Source Learning Companion",



    version="0.1.0",



)











# Initialize the SQLite database when the backend starts.



initialize_database()











# Allow the frontend to communicate with the backend.



# For local development only; restrict origins before deployment.



app.add_middleware(



    CORSMiddleware,



    allow_origins=["*"],



    allow_methods=["*"],



    allow_headers=["*"],



)











# ============================================================



# TEMPORARY DOCUMENT STORAGE



# ============================================================







# Documents are stored in memory while the backend is running.



# This is temporary storage for the current development phase.



DOCUMENT_STORE: dict[str, dict] = {}





# Generated quizzes are stored temporarily while the backend is running.

QUIZ_STORE: dict[str, dict] = {}











# ============================================================



# BASIC ENDPOINTS



# ============================================================







@app.get("/")



def home():



    return {"message": "Welcome to StudyBuddy AI!"}











@app.get("/health")



def health_check():



    return {



        "status": "healthy",



        "app": "StudyBuddy AI",



    }











# ============================================================



# PDF DOCUMENT UPLOAD



# ============================================================







MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB











@app.post("/documents")



async def upload_document(file: UploadFile = File(...)):







    # Validate file type.



    if file.content_type != "application/pdf":



        raise HTTPException(



            status_code=400,



            detail="Only PDF files are supported.",



        )







    # Read the uploaded file.



    file_bytes = await file.read()







    # Validate file size.



    if len(file_bytes) > MAX_FILE_SIZE:



        raise HTTPException(



            status_code=413,



            detail="PDF file is too large. Maximum size is 10 MB.",



        )







    if not file_bytes:



        raise HTTPException(



            status_code=400,



            detail="The uploaded PDF is empty.",



        )







    try:



        # Extract text from the PDF.



        pages = extract_pdf_text(file_bytes)







    except Exception as exc:



        print(



            f"PDF extraction error: "



            f"{type(exc).__name__}: {exc}"



        )







        raise HTTPException(



            status_code=400,



            detail="Could not extract text from the PDF.",



        ) from exc







    total_characters = sum(



        len(page["text"])



        for page in pages



    )







    # Split extracted text into chunks.



    chunks = chunk_pages(pages)







    # Create a unique ID for this document.



    document_id = str(uuid4())







    # Store the document and its chunks temporarily.



    DOCUMENT_STORE[document_id] = {



        "filename": file.filename,



        "size": len(file_bytes),



        "pages": len(pages),



        "characters": total_characters,



        "chunks": chunks,



    }







    return {



        "document_id": document_id,



        "filename": file.filename,



        "size": len(file_bytes),



        "pages": len(pages),



        "characters": total_characters,



        "chunk_count": len(chunks),



        "status": "uploaded",



    }











# ============================================================



# DOCUMENT QUESTION ANSWERING



# ============================================================







class DocumentQuestionRequest(BaseModel):



    document_id: str = Field(



        min_length=1,



        max_length=100,



    )







    question: str = Field(



        min_length=1,



        max_length=2000,



    )











@app.post("/documents/ask")



def ask_document(request: DocumentQuestionRequest):







    # Find the uploaded document.



    document = DOCUMENT_STORE.get(



        request.document_id



    )







    if document is None:



        raise HTTPException(



            status_code=404,



            detail="Document not found. Please upload the PDF again.",



        )







    try:



        result = answer_from_document(



            question=request.question,



            chunks=document["chunks"],



            top_k=3,



        )







        return {



            "document_id": request.document_id,



            "filename": document["filename"],



            "question": request.question,



            "answer": result["answer"],



            "sources": result["sources"],



            "status": "success",



        }







    except AIProviderTimeoutError as exc:



        raise HTTPException(



            status_code=504,



            detail=(



                "The AI tutor took too long to answer. "



                "Please try again."



            ),



        ) from exc







    except AIProviderError as exc:



        raise HTTPException(



            status_code=502,



            detail=(



                "The AI tutor is temporarily unavailable. "



                "Please try again."



            ),



        ) from exc







    except Exception as exc:



        print(



            f"Unexpected document question error: "



            f"{type(exc).__name__}: {exc}"



        )







        raise HTTPException(



            status_code=500,



            detail="An unexpected server error occurred.",



        ) from exc











# ============================================================



# AI QUIZ GENERATION



# ============================================================







class QuizRequest(BaseModel):



    document_id: str = Field(



        min_length=1,



        max_length=100,



    )







    topic: str = Field(



        default="",



        max_length=200,



    )







    number_of_questions: int = Field(



        default=5,



        ge=1,



        le=10,



    )











@app.post("/quizzes/generate")



def generate_quiz_endpoint(request: QuizRequest):







    # Find the uploaded document.



    document = DOCUMENT_STORE.get(



        request.document_id



    )







    if document is None:



        raise HTTPException(



            status_code=404,



            detail="Document not found. Please upload the PDF again.",



        )







    # Use the document filename if no topic was provided.



    topic = request.topic.strip()







    if not topic:



        topic = document["filename"]







    try:



        # Pass the document chunks to the quiz service.



        # The quiz service will retrieve chunks relevant



        # to the requested topic before calling Gemma.



        quiz = generate_quiz(



            topic=topic,



            chunks=document["chunks"],



            number_of_questions=request.number_of_questions,



        )







        quiz_id = str(uuid4())



        QUIZ_STORE[quiz_id] = {

            "document_id": request.document_id,

            "filename": document["filename"],

            "topic": topic,

            "quiz": quiz,

        }



        return {



            "quiz_id": quiz_id,

            "document_id": request.document_id,



            "filename": document["filename"],



            "topic": topic,



            "number_of_questions": len(quiz),



            "quiz": quiz,



            "status": "success",



        }







    except AIProviderTimeoutError as exc:



        raise HTTPException(



            status_code=504,



            detail=(



                "The AI quiz generator took too long to respond. "



                "Please try again."



            ),



        ) from exc







    except AIProviderError as exc:



        raise HTTPException(



            status_code=502,



            detail=(



                "The AI quiz generator is temporarily unavailable. "



                "Please try again."



            ),



        ) from exc







    except Exception as exc:



        print(



            f"Unexpected quiz generation error: "



            f"{type(exc).__name__}: {exc}"



        )







        raise HTTPException(



            status_code=500,



            detail="Could not generate the quiz.",



        ) from exc











# ============================================================



# QUIZ ATTEMPT PERSISTENCE



# ============================================================







class QuizAttemptRequest(BaseModel):



    document_id: str = Field(



        min_length=1,



        max_length=100,



    )







    topic: str = Field(



        default="",



        max_length=200,



    )







    total_questions: int = Field(



        ge=1,



        le=10,



    )







    correct_answers: int = Field(



        ge=0,



        le=10,



    )











@app.post("/quizzes/attempts")



def save_quiz_attempt_endpoint(



    request: QuizAttemptRequest,



):







    # Find the uploaded document.



    document = DOCUMENT_STORE.get(



        request.document_id



    )







    if document is None:



        raise HTTPException(



            status_code=404,



            detail="Document not found. Please upload the PDF again.",



        )







    # Validate the score.



    if request.correct_answers > request.total_questions:



        raise HTTPException(



            status_code=400,



            detail=(



                "Correct answers cannot exceed "



                "total questions."



            ),



        )







    # Use the document filename if no topic was provided.



    topic = request.topic.strip()







    if not topic:



        topic = document["filename"]







    try:



        attempt_id = save_quiz_attempt(



            document_id=request.document_id,



            filename=document["filename"],



            topic=topic,



            total_questions=request.total_questions,



            correct_answers=request.correct_answers,



        )







        score_percentage = (



            request.correct_answers



            / request.total_questions



        ) * 100







        return {



            "attempt_id": attempt_id,



            "document_id": request.document_id,



            "filename": document["filename"],



            "topic": topic,



            "total_questions": request.total_questions,



            "correct_answers": request.correct_answers,



            "score_percentage": score_percentage,



            "status": "saved",



        }







    except ValueError as exc:



        raise HTTPException(



            status_code=400,



            detail=str(exc),



        ) from exc







    except Exception as exc:



        print(



            f"Unexpected quiz attempt error: "



            f"{type(exc).__name__}: {exc}"



        )







        raise HTTPException(



            status_code=500,



            detail="Could not save the quiz attempt.",



        ) from exc











# ============================================================



# ============================================================

# QUIZ SUBMISSION

# ============================================================



class QuizSubmitRequest(BaseModel):

    answers: list[str] = Field(

        min_length=1,

        max_length=10,

    )





@app.post("/quizzes/{quiz_id}/submit")

def submit_quiz(

    quiz_id: str,

    request: QuizSubmitRequest,

):



    quiz_data = QUIZ_STORE.get(quiz_id)



    if quiz_data is None:

        raise HTTPException(

            status_code=404,

            detail="Quiz not found. Please generate the quiz again.",

        )



    quiz = quiz_data["quiz"]



    if len(request.answers) != len(quiz):

        raise HTTPException(

            status_code=400,

            detail=(

                "The number of submitted answers must match "

                "the number of quiz questions."

            ),

        )



    results = []

    correct_answers = 0



    for index, question in enumerate(quiz):

        selected_answer = request.answers[index]

        correct_answer = question["correct_answer"]

        is_correct = selected_answer == correct_answer



        if is_correct:

            correct_answers += 1



        results.append({

            "question_number": index + 1,

            "selected_answer": selected_answer,

            "correct_answer": correct_answer,

            "is_correct": is_correct,

            "explanation": question["explanation"],

        })



    total_questions = len(quiz)

    score_percentage = (

        correct_answers / total_questions

    ) * 100



    try:

        attempt_id = save_quiz_attempt(

            document_id=quiz_data["document_id"],

            filename=quiz_data["filename"],

            topic=quiz_data["topic"],

            total_questions=total_questions,

            correct_answers=correct_answers,

        )



        return {

            "quiz_id": quiz_id,

            "attempt_id": attempt_id,

            "topic": quiz_data["topic"],

            "total_questions": total_questions,

            "correct_answers": correct_answers,

            "score_percentage": score_percentage,

            "results": results,

            "status": "submitted",

        }



    except ValueError as exc:

        raise HTTPException(

            status_code=400,

            detail=str(exc),

        ) from exc



    except Exception as exc:

        print(

            f"Unexpected quiz submission error: "

            f"{type(exc).__name__}: {exc}"

        )



        raise HTTPException(

            status_code=500,

            detail="Could not submit the quiz.",

        ) from exc





# ============================================================

# QUIZ HISTORY

# ============================================================



@app.get("/quizzes/attempts")

def get_quiz_attempts_endpoint():



    try:

        attempts = get_quiz_attempts()



        return {

            "attempts": attempts,

            "count": len(attempts),

            "status": "success",

        }



    except Exception as exc:

        print(

            f"Unexpected quiz history error: "

            f"{type(exc).__name__}: {exc}"

        )



        raise HTTPException(

            status_code=500,

            detail="Could not retrieve quiz history.",

        ) from exc





# ============================================================
# FLASHCARD GENERATION
# ============================================================


class FlashcardRequest(BaseModel):
    document_id: str = Field(
        min_length=1,
        max_length=100,
    )

    topic: str = Field(
        default="",
        max_length=200,
    )

    number_of_cards: int = Field(
        default=5,
        ge=1,
        le=10,
    )


@app.post("/flashcards/generate")
def generate_flashcards_endpoint(request: FlashcardRequest):

    document = DOCUMENT_STORE.get(request.document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload the PDF again.",
        )

    topic = request.topic.strip()

    if not topic:
        topic = document["filename"]

    try:
        flashcards = generate_flashcards(
            topic=topic,
            chunks=document["chunks"],
            number_of_cards=request.number_of_cards,
        )

        return {
            "document_id": request.document_id,
            "filename": document["filename"],
            "topic": topic,
            "number_of_cards": len(flashcards),
            "flashcards": flashcards,
            "status": "success",
        }

    except AIProviderTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=(
                "The AI flashcard generator took too long to respond. "
                "Please try again."
            ),
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI flashcard generator is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    except Exception as exc:
        print(
            f"Unexpected flashcard generation error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Could not generate flashcards.",
        ) from exc


# STUDY NOTES



# ============================================================







class StudyNotesRequest(BaseModel):



    topic: str = Field(



        min_length=1,



        max_length=200,



    )







    difficulty: str = Field(



        default="beginner",



        max_length=50,



    )











@app.post("/study-notes")



def generate_study_notes(request: StudyNotesRequest):







    prompt = f"""



You are StudyBuddy AI, a friendly and patient study tutor.







Create study notes about the topic below.







Topic:



{request.topic}







Difficulty level:



{request.difficulty}







Follow these rules:







1\. Start with a clear title.



2\. Give a simple definition or introduction.



3\. Explain the important concepts.



4\. Use bullet points where useful.



5\. Include a short Python code example if the topic is related to programming.



6\. Explain the code briefly.



7\. End with a short "Key Takeaways" section.



8\. Keep the explanation focused and beginner-friendly.



9\. Avoid unnecessary repetition.







Return only the study notes.



"""







    try:



        notes = get_ai_response(prompt)







        return {



            "topic": request.topic,



            "difficulty": request.difficulty,



            "notes": notes,



            "status": "success",



        }







    except AIProviderTimeoutError as exc:



        raise HTTPException(



            status_code=504,



            detail=(



                "The AI tutor took too long to generate the study notes. "



                "Please try again."



            ),



        ) from exc







    except AIProviderError as exc:



        raise HTTPException(



            status_code=502,



            detail=(



                "The AI tutor is temporarily unavailable. "



                "Please try again."



            ),



        ) from exc







    except Exception as exc:



        print(



            f"Unexpected study notes error: "



            f"{type(exc).__name__}: {exc}"



        )







        raise HTTPException(



            status_code=500,



            detail="An unexpected server error occurred.",



        ) from exc