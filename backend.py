def handle_upload(request):
    excel_file = request.files.get('excel_file')
    user_question = request.form.get('user_question')
    print("Form Data Has Been Received!")
    print(f"User Question: {user_question}")

    if excel_file:
        print(f"File Name: {excel_file.filename}")
        print(f"File Content Type: {excel_file.content_type}")
    else:
        print("No file uploaded")

    return f"<h2>Data Received!</h2><p>Question: {user_question}</p><p>File: {excel_file or 'No File'}</p>"
