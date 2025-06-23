import pandas as pd
import openpyxl
import google.generativeai as genai
import os
from flask import session, redirect, url_for
from markupsafe import Markup
from io import BytesIO
import uuid
import re
import markdown as md

UPLOAD_FOLDER = 'tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def format_dataframe_for_display(df, max_rows_display=25):
    if len(df) <= max_rows_display * 2:  # If small enough to show all
        html_output = df.to_html(index=False,
                                 classes='table table-striped',
                                 border=0)
    else:
        html_output = df.head(max_rows_display).to_html(
            index=False, classes='table table-striped', border=0)
        html_output += "<br>"
        html_output += df.tail(max_rows_display).to_html(
            index=False, classes='table table-striped', border=0)
    return html_output


def get_gemini_client():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')


def get_gemini_response(file_data, user_question="", chat_history=None):
    model = get_gemini_client()
    if not model:
        return "Please use a Gemini API key to access this feature."
    if chat_history:
        history_str = "\n".join([
            f"User: {q['question']}\nAssistant: {q['answer']}"
            for q in chat_history
        ])
        prompt = f"""
You are an expert, friendly, and proactive Excel assistant. Your job is to help the user interpret, analyze, and get the most out of their uploaded Excel file. Use your knowledge of spreadsheets, formulas, and data analysis to provide clear, CONCISE, actionable, and conversational answers.

Below is the Excel Data Preview (this can be the full file content for smaller files, or a summary for larger files), followed by the chat history and the user's latest question.

Excel Data Preview:
{file_data}

Chat History:
{history_str}

User's New Question:
{user_question}

Instructions:
- Occasionally (especially early in the conversation or when relevant), offer proactive insights, trends, or suggestions based on the data. Do not repeat the same types of insights in every response. If the user's question is specific, focus on answering it directly.
- If the data contains dates or time periods, you may perform trend analysis (e.g., month-over-month, year-over-year changes) and summarize the results, but only if it hasn't already been done recently.
- When applicable, automatically calculate and present key business metrics or financial ratios.
- When asked a question, also provide the Excel formulas or step-by-step instructions for the user to perform the task themselves.
- For step-by-step instructions, always use Markdown bullet points (e.g., * Item 1\n* Item 2).
- Reference specific columns, rows, or values when helpful.
- If the user's request is unclear, ask a clarifying question.
- Be as concise and brief as possible while remaining helpful and thorough. Aim for direct answers.
- Avoid unnecessary disclaimers.
- Do not generate tables in your response. If you need to summarize differences or comparisons, use bullet points or plain text instead of tables.

Respond as a helpful, proactive Excel assistant.
"""
    else:
        prompt = f"""
You are an expert, friendly, and proactive Excel assistant. Your job is to help the user interpret, analyze, and get the most out of their uploaded Excel file. Use your knowledge of spreadsheets, formulas, and data analysis to provide clear, CONCISE, actionable, and conversational answers.

Below is the Excel Data Preview (this can be the full file content for smaller files, or a summary for larger files), followed by the user's question.

Excel Data Preview:
    {file_data}

User's Question:
{user_question}

Instructions:
- Occasionally (especially early in the conversation or when relevant), offer proactive insights, trends, or suggestions based on the data. Do not repeat the same types of insights in every response. If the user's question is specific, focus on answering it directly.
- If the data contains dates or time periods, you may perform trend analysis (e.g., month-over-month, year-over-year changes) and summarize the results, but only if it hasn't already been done recently.
- When applicable, automatically calculate and present key business metrics or financial ratios.
- When asked a question, also provide the Excel formulas or step-by-step instructions for the user to perform the task themselves.
- For step-by-step instructions, always use Markdown bullet points (e.g., * Item 1\n* Item 2).
- Reference specific columns, rows, or values when helpful.
- If the user's request is unclear, ask a clarifying question.
- Be as concise and brief as possible while remaining helpful and thorough. Aim for direct answers.
- Avoid unnecessary disclaimers.
- Do not generate tables in your response. If you need to summarize differences or comparisons, use bullet points or plain text instead of tables.

Respond as a helpful, proactive Excel assistant.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI API Error: {e}")
        return "The AI service is currently unavailable, please try again later."


def summarize_dataframe(df, max_rows=100):
    summary = []
    summary.append(f"Columns: {', '.join(df.columns.astype(str))}")
    summary.append(
        "Column types: " +
        ', '.join([f"{col}: {dtype}" for col, dtype in df.dtypes.items()]))
    try:
        summary.append("Summary statistics:\n" +
                       df.describe(include='all').to_string())
    except Exception:
        pass
    if len(df) <= max_rows:
        summary.append("Full data:\n" + df.to_string())
    else:
        summary.append("Sample rows (first 10):\n" + df.head(10).to_string())
        summary.append("Sample rows (last 10):\n" + df.tail(10).to_string())
    return '\n\n'.join(summary)


def handle_upload(request):
    excel_file = request.files.get('excel_file')
    user_question = request.form.get('user_question')

    
    excel_file.seek(0, os.SEEK_END)
    file_size = excel_file.tell()
    excel_file.seek(0) # Reset file pointer
    if file_size > 10 * 1024 * 1024:
        print(f"Backend Check Failed: File size ({file_size / (1024*1024):.2f}MB) exceeds 10MB limit. User redirected.")
        return redirect(url_for('index'))

    filename = excel_file.filename.lower()
    file_extension = os.path.splitext(filename)[1]
    if file_extension not in ['.xls', '.xlsx']:
        print(f"Backend Check Failed: Invalid file type uploaded ('{file_extension}'). User redirected.")
        return redirect(url_for('index'))

    unique_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_FOLDER, unique_id + file_extension)
    excel_file.save(save_path)
    session['excel_file_path'] = save_path
    session['excel_file_name'] = excel_file.filename
    session['excel_file_ext'] = file_extension
    
    try:
        xls = pd.ExcelFile(save_path)
        sheet_names = xls.sheet_names
        current_sheet = sheet_names[0]
        session['sheet_names'] = sheet_names
        session['current_sheet'] = current_sheet
        df = pd.read_excel(save_path, sheet_name=current_sheet)
    except Exception as e:
        print(f"Backend Check Failed: Could not read Excel file. Error: {e}. User redirected.")
        return redirect(url_for('index'))
    
    session['chat_history'] = []
    
    file_summary = summarize_dataframe(df)
    gemini_response = get_gemini_response(file_summary, user_question)
    
    session['chat_history'].append({'question': user_question, 'answer': gemini_response})
    session['file_preview_html'] = format_dataframe_for_display(df)
    
    return redirect(url_for('chat'))


def handle_chat(request):
    file_path = session.get('excel_file_path')
    if not file_path or not os.path.exists(file_path):
        return redirect(url_for('index'))

    # Handle state changes on POST requests
    if request.method == 'POST':
        # User changed the sheet
        if request.form.get('action') == 'change_sheet':
            new_sheet = request.form.get('sheet_selection')
            if new_sheet in session.get('sheet_names', []):
                session['current_sheet'] = new_sheet
                session['chat_history'] = []  # Clear chat history
        
        # User asked a new question
        elif user_question := request.form.get('user_question'):
            current_sheet = session.get('current_sheet')
            try:
                df = pd.read_excel(file_path, sheet_name=current_sheet)
            except Exception as e:
                print(f"Backend Check Failed in /chat: Could not read Excel file. Error: {e}. User redirected.")
                return redirect(url_for('index'))
            file_summary = summarize_dataframe(df)
            chat_history = session.get('chat_history', [])
            gemini_response = get_gemini_response(file_summary, user_question, chat_history)
            gemini_response = re.sub(r'^\s*DocuBridge Assistant:\s*', '', gemini_response, flags=re.IGNORECASE)
            chat_history.append({'question': user_question, 'answer': gemini_response})
            session['chat_history'] = chat_history

        # After any POST action, redirect to the GET endpoint to render the page
        return redirect(url_for('chat'))

    # Handle page rendering on GET requests
    current_sheet = session.get('current_sheet')
    try:
        df = pd.read_excel(file_path, sheet_name=current_sheet)
    except Exception as e:
        print(f"Backend Check Failed in /chat: Could not read Excel file. Error: {e}. User redirected.")
        return redirect(url_for('index'))
    file_preview_html = format_dataframe_for_display(df)
    sheet_names = session.get('sheet_names', [])
    chat_history = session.get('chat_history', [])
    
    # Determine input placeholder
    if len(chat_history) == 0:
        input_placeholder = "Ask a question..."
    else:
        input_placeholder = "Ask a follow up question..."
    
    # Build chat history HTML
    chat_html = ''
    for entry in chat_history:
        html_answer = md.markdown(entry['answer'])
        chat_html += f'''
        <div class="chat-bubble user"><strong>You:</strong> {Markup.escape(entry['question'])}</div>
        <div class="chat-bubble bot"><strong>DocuBridge Assistant:</strong> {html_answer}</div>
        '''
    
    # Build sheet selector HTML if multiple sheets exist
    sheet_selector_html = ''
    if len(sheet_names) > 1:
        options = ''
        for name in sheet_names:
            selected = 'selected' if name == current_sheet else ''
            options += f'<option value="{name}" {selected}>{name}</option>'
        
        sheet_selector_html = f'''
        <div class="sheet-selector">
            <form method="POST" action="/chat" id="sheetForm">
                <input type="hidden" name="action" value="change_sheet">
                <label for="sheet_selection">Select Sheet:</label>
                <select name="sheet_selection" id="sheet_selection" onchange="this.form.submit()">
                    {options}
                </select>
                <small>Changing sheets will clear the chat history.</small>
            </form>
        </div>
        '''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DocuBridge - Chat</title>
        <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap' rel='stylesheet'>
        <style>
            body {{
                background-color: #f5f7fa;
                color: #2c3e50;
                font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 1rem 2rem 2rem 2rem;
            }}
            .container {{
                max-width: 800px;
                margin: 1.2rem auto 2rem auto;
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(44, 62, 80, 0.08);
                padding: 1.5rem 2rem 2rem 2rem;
            }}
            h2 {{
                text-align: center;
                color: #2c3e50;
                font-size: 2.2rem;
                margin-bottom: 1.2rem;
            }}
            h3 {{
                color: #3498db;
                margin-top: 2rem;
                margin-bottom: 0.5rem;
                font-size: 1.2rem;
            }}
            h4 {{
                color: #2c3e50;
                margin-top: 1rem;
                margin-bottom: 0.3rem;
                font-size: 1.1rem;
            }}
            .sheet-selector {{
                margin-bottom: 1.5rem;
                background: #f8fafc;
                border-radius: 8px;
                padding: 1rem 1.2rem;
                border: 1px solid #e0e6ed;
            }}
            .sheet-selector form {{
                display: flex;
                align-items: center;
                gap: 1rem;
                margin: 0;
            }}
            .sheet-selector label {{
                font-weight: 600;
            }}
            .sheet-selector select {{
                padding: 0.5rem;
                border-radius: 5px;
                border: 1px solid #e0e6ed;
            }}
            .sheet-selector small {{
                color: #7f8c8d;
            }}
            .file-info {{
                margin-bottom: 1.5rem;
                background: #f8fafc;
                border-radius: 8px;
                padding: 1rem 1.2rem;
                border: 1px solid #e0e6ed;
                max-width: 100%;
                overflow-x: auto;
                max-height: 340px;
                min-height: 80px;
                box-sizing: border-box;
            }}
            .file-info ul {{
                list-style: none;
                padding-left: 0;
            }}
            .file-info ul li {{
                margin-bottom: 0.2rem;
            }}
            .file-info table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 0.5rem;
                background: #fff;
                border-radius: 6px;
                overflow: hidden;
                font-size: 0.9rem;
            }}
            .file-info th, .file-info td {{
                border: 1px solid #e0e6ed;
                padding: 0.5rem 0.7rem;
                text-align: left;
            }}
            .file-info th {{
                background: #eaf3fa;
                color: #2980b9;
                font-weight: 700;
            }}
            .chat-container {{
                background: #f8fafc;
                border-radius: 8px;
                border: 1px solid #e0e6ed;
                padding: 1rem;
                max-height: 320px;
                overflow-y: auto;
                margin-bottom: 1.2rem;
                display: flex;
                flex-direction: column;
                gap: 0.7rem;
            }}
            .chat-bubble {{
                padding: 0.7rem 1rem;
                border-radius: 8px;
                max-width: 90%;
                word-break: break-word;
                font-size: 1.05rem;
            }}
            .chat-bubble.user {{
                background: #eaf3fa;
                align-self: flex-end;
                color: #2c3e50;
            }}
            .chat-bubble.bot {{
                background: #f0e6fa;
                align-self: flex-start;
                color: #34495e;
            }}
            .chat-bubble.typing {{
                background: #f9f9f9;
                align-self: flex-start;
                color: #888;
                font-style: italic;
                opacity: 0.8;
            }}
            form {{
                display: flex;
                gap: 0.7rem;
                margin-top: 0.5rem;
            }}
            input[type="text"] {{
                flex: 1;
                padding: 0.8rem;
                border: 1px solid #e0e6ed;
                border-radius: 5px;
                font-size: 1rem;
            }}
            button {{
                background-color: #3498db;
                color: white;
                padding: 0.8rem 1.5rem;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
                transition: background-color 0.3s ease;
            }}
            button:hover {{
                background-color: #2980b9;
            }}
            button:disabled {{
                background-color: #7ba6c7;
                cursor: not-allowed;
                opacity: 0.7;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 1.5rem;
                color: #3498db;
                text-decoration: none;
                font-weight: 600;
                transition: color 0.2s;
            }}
            .back-link:hover {{
                color: #217dbb;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>DocuBridge Chat</h2>
            {sheet_selector_html}
            <h3>File Data Preview</h3>
            <div class="file-info">
                {file_preview_html}
            </div>
            <h3>Chat</h3>
            <div class="chat-container" id="chatContainer">
                {chat_html}
            </div>
            <form method="POST" action="/chat" id="chatForm">
                <input type="text" name="user_question" placeholder="{input_placeholder}" autocomplete="off" required id="userQuestionInput" />
                <button type="submit" id="sendBtn">Send</button>
            </form>
            <a href="/" class="back-link">&larr; Back to Home</a>
        </div>
        <script>
            // Auto-scroll chat to bottom
            var chatDiv = document.getElementById('chatContainer');
            if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;

            // Show 'DocuBridge Assistant is typing...' indicator on form submit
            document.getElementById('chatForm').addEventListener('submit', function(e) {{
                var chatDiv = document.getElementById('chatContainer');
                var typingBubble = document.createElement('div');
                typingBubble.className = 'chat-bubble bot typing';
                typingBubble.innerHTML = '<strong>DocuBridge Assistant:</strong> <span id="typingDots">.</span> DocuBridge Assistant is typing...';
                chatDiv.appendChild(typingBubble);
                chatDiv.scrollTop = chatDiv.scrollHeight;
                // Animate the dots
                var dots = document.getElementById('typingDots');
                var dotCount = 1;
                var interval = setInterval(function() {{
                    dotCount = (dotCount % 3) + 1;
                    dots.textContent = '.'.repeat(dotCount);
                }}, 500);
                // Disable input and button while waiting for response
                document.getElementById('userQuestionInput').readOnly = true;
                document.getElementById('sendBtn').disabled = true;
            }});
        </script>
    </body>
    </html>
        """
