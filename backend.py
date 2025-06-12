import pandas as pd
import openpyxl
import openai
import os

# Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    return openai.OpenAI(api_key=api_key)

def get_chatgpt_response(file_data, user_question, custom_prompt=""):
    client = get_openai_client()
    if not client:
        return "OpenAI API key not configured. Please add your API key to the secrets."
    
    # Prepare the prompt with file data and user question
    system_prompt = f"""
    {custom_prompt}
    
    You are an AI assistant that analyzes financial data and answers questions about it.
    Below is data from an uploaded Excel file, followed by a user question.
    
    File Data (first 10 rows):
    {file_data}
    
    User Question: {user_question}
    
    Please provide a helpful and accurate response based on the data provided.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting ChatGPT response: {str(e)}"

def handle_upload(request):
    excel_file = request.files.get('excel_file')
    user_question = request.form.get('user_question')
    if excel_file and user_question:
        df = pd.read_excel(excel_file)
    else:
        missingParameters = []
        if not excel_file:
            missingParameters.append("excel file")
        if not user_question:
            missingParameters.append("user question")
        return f"<h2>Incomplete Form Data Was Received!</h2><p>Please provide the following missing parameters: {', '.join(missingParameters)}</p>"            

    if excel_file:
        print(f"File Name: {excel_file.filename}")
        print(f"File Content Type: {excel_file.content_type}")
        
        # Get ChatGPT response
        file_preview = df.head(10).to_string()
        chatgpt_response = get_chatgpt_response(file_preview, user_question)
        
        return f"""
        <h2>Analysis Complete!</h2>
        <h3>Your Question:</h3>
        <p>{user_question}</p>
        <h3>ChatGPT Response:</h3>
        <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0; background-color: #f9f9f9;">
            {chatgpt_response}
        </div>
        <h3>File Data Preview:</h3>
        <p><strong>File:</strong> {excel_file.filename}</p>
        {df.head().to_html()}
        """
    else:
        print("No file uploaded")

    return f"<h2>Data Received!</h2><p>Question: {user_question if user_question else 'No Question Was Submitted'}</p><p>File: No File Was Submitted</p>"
