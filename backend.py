
def handle_upload(request):
    # Get the uploaded file
    excel_file = request.files.get('excel_file')
    
    # Get the user question
    user_question = request.form.get('user_question')
    
    # Log the inputs to console
    print("=== Form Data Received ===")
    print(f"User Question: {user_question}")
    
    if excel_file:
        print(f"File Name: {excel_file.filename}")
        print(f"File Content Type: {excel_file.content_type}")
    else:
        print("No file uploaded")
    
    print("========================")
    
    # Return a simple response
    return f"<h2>Data Received!</h2><p>Question: {user_question}</p><p>File: {excel_file.filename if excel_file else 'No file'}</p>"
