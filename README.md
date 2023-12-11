# Document GPT - Setup and Usage Guide
This guide will walk you through the setup and usage of Document GPT.

```
Note: This version supports only PDF files. 
```

## Prerequisites
Before you begin, ensure you have the following installed on your system:
    
    Python (version 3.6 or higher)
    pip (Python package manager)
    
## Installation
Clone the repository to your local machine using the following command:<br>
    
    git clone https://github.com/your-username/your-repo-name.git
    

Navigate to the project directory:<br>
    
    cd your-repo-name

Create a virtual environment. Run the below command from project directory.

    python -m venv <env_name>

Activate the enviroment

    For windows
    .\\env_name\\Scripts\\Activate

    For linux
    source env_name/bin/activate

Install the required Python packages by running:<br>
    
    pip install -r requirements.txt


## Configuration
Open the config.yaml file and add the following configuration information:

    OPENAI_API_KEY: "your_api_key"

Replace your_api_key with your actual OpenAI API key.

## Usage
Run the chroma database from the termial using the following command:<br>

    chroma run --path 'storage'

To run the app file, use the following command:<br>

    cd frontend
    streamlit run app.py


The program will will open a chat UI in you web browser. Type your message and press Enter.

The program will retrieve a response from ChromaDB based on your input and display it as the assistant's response.

You can continue the conversation by entering more messages.

To exit the program, go to termial press Ctrl+C.