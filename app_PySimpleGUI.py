# Import the required libraries
import PyPDF2
import requests
import PySimpleGUI as sg
import os
import openai

# Define a class for the PDF Summarizer
class PDFSummarizer:
    # Define the instance variables for the class
    def __init__(self):
        self.pdf_file = None
        self.pdf_reader = None
        self.num_pages = 0
        self.start_page = 0
        self.end_page = 0
        self.text = ''
        self.summary=''

    # Open the PDF file
    def open_pdf_file(self, file_path):
        self.pdf_file = open(file_path, 'rb')
        self.pdf_reader = PyPDF2.PdfReader(self.pdf_file)
        self.num_pages = len(self.pdf_reader.pages)
        
    # Close the PDF file
    def close_pdf_file(self):
        if self.pdf_file is not None:
            self.pdf_file.close()
        self.pdf_reader = None
        self.num_pages = 0

    # Set the starting and ending page numbers
    def set_start_page(self, start_page):
        end_page=start_page.split("-")[1]
        start_page=start_page.split("-")[0]
        if(start_page==''):
            start_page=1
        self.start_page = int(start_page) - 1
        self.end_page = int(end_page) - 1

    # Extract the text from the selected pages of the PDF
    def extract_text_func(self):
        self.text = ''
        for page_num in range(self.start_page, self.end_page):
            page = self.pdf_reader.pages[page_num]
            self.text += page.extract_text()
            self.summary += self.summarize_text(page.extract_text())

    # Run the OpenAI summarization model
    def OpenAIrun(self, prompt):
        # Change the current working directory
        os.chdir("path for API key")
        # Open the API key file
        file1 = open("key.txt","r+")
        # Read the API key
        api_key=file1.read()
        # Set the OpenAI API key
        openai.organization="OpenAI org id"
        openai.api_key = api_key
        
        # Set the model parameters and generate the summary using OpenAI API
        response = openai.Completion.create(
        engine="davinci-instruct-beta-v3",
        prompt=prompt,
        temperature=0.8,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

        if 'choices' in response:
            if len(response['choices']) > 0:
                ret = response['choices'][0]['text']
            else:
                ret = 'No responses'
        else:
            ret = 'No responses'

        return ret
    
    # Summarize the text using the OpenAI model
    def summarize_text(self, text):
        # Set the prompt for the summarization model
        prompt = f'Summarize the following text in maximum of 50 words:\n{text}',
        # Call the OpenAIrun method to generate the summary
        try:
            summary = self.OpenAIrun(prompt)
            #print(f'Response : {summary}')
        except Exception as e:
            summary={str(e)}
            #print(f'Exception : {str(e)}')

        return summary.strip()
    

# Define the layout of the PySimpleGUI window

out_col1=[[sg.Text('Input')],[sg.Output(size=(80, 20),key='out_input')]]
out_col2=[[sg.Text('Summary')],[sg.Output(size=(80, 20),key='out_summary')]]

layout = [
    [sg.Text('Select a PDF file:')],
    [sg.Input(key='pdf_file'), sg.FileBrowse()],
    [sg.Button('Count pages')],
    [sg.Text('Enter starting page:')],
    [sg.Input(key='start_page')],
    [sg.Button('Summarize')],
    [sg.Column(out_col1),
     sg.Column(out_col2)]
]

# Create the PySimpleGUI window
window = sg.Window('PDF Summarizer', layout)

# Create an instance of the PDFSummarizer class
pdf_summarizer = PDFSummarizer()

# Start the event loop for the window
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED:
        break
    if event == 'Count pages':
        pdf_summarizer.open_pdf_file(values['pdf_file'])
        num_pages = pdf_summarizer.num_pages
        pdf_summarizer.close_pdf_file()
        sg.popup(f'The PDF file has {num_pages} pages.')

    if event == 'Summarize':
        pdf_summarizer.open_pdf_file(values['pdf_file'])
        pdf_summarizer.set_start_page(values['start_page'])
        pdf_summarizer.extract_text_func()
        #summary = pdf_summarizer.summarize_text()

        pdf_summarizer.close_pdf_file()
        #print(pdf_summarizer.text)
        #print(summary)
        window['out_input'].update(pdf_summarizer.text)
        window['out_summary'].update(pdf_summarizer.summary)

window.close()
