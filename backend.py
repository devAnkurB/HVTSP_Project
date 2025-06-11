import pandas as pd
import openpyxl

def handle_upload(request):
    excel_file = request.files.get('excel_file')
    if excel_file:
        df = pd.read_excel(excel_file)
        print("Form Data Has Been Received!")
    else:
        return ("No Form Data Has Been Received!")
    user_question = request.form.get('user_question')
    print(f"User Question: {user_question}")

    if excel_file:
        print(f"File Name: {excel_file.filename}")
        print(f"File Content Type: {excel_file.content_type}")
    else:
        print("No file uploaded")

    return f"<h2>Data Received!</h2><p>Question: {user_question if user_question else 'No Question Was Submitted'}</p><p>File: {df.head().to_html(), excel_file.filename if excel_file else 'No File Was Submitted'}</p>"
