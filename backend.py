import pandas as pd
import openpyxl


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
    else:
        print("No file uploaded")

    return f"<h2>Data Received!</h2><p>Question: {user_question if user_question else 'No Question Was Submitted'}</p><p>File: {df.head().to_html(), excel_file.filename if excel_file else 'No File Was Submitted'}</p>"
