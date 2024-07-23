# README

## Overview

This project is a Streamlit-based web application that utilizes Google Gemini's Generative AI to convert natural language questions into SQL queries and retrieve data from a PostgreSQL database. The application also provides a paraphrased response to the SQL query results.

## Features

1. **Natural Language to SQL Conversion:** Convert English questions into SQL queries using Google Gemini's Generative AI.
2. **SQL Query Execution:** Execute the generated SQL queries on a PostgreSQL database.
3. **Response Paraphrasing:** Provide a well-formulated paraphrased response to the SQL query results.
4. **User Interface:** A Streamlit web interface for users to input questions and receive responses.

## Requirements

- Python 3.8 or higher
- PostgreSQL database
- Streamlit
- Pandas
- SQLAlchemy
- Google Gemini AI (Google Generative AI)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/jawadoch/nlp2sql.git
cd your-project
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

Create a `.env` file in the project root directory and add your environment variables:

```plaintext
GOOGLE_API_KEY=your_google_api_key
```

## Usage

1. Start the Streamlit app:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Input your question in natural language and click the "Ask the question" button.

4. The app will display the generated SQL query, the query results, and a paraphrased response.

## Project Structure

- `app.py`: The main application file containing the Streamlit app and logic for interacting with Google Gemini AI and the PostgreSQL database.
- `requirements.txt`: The list of required Python packages.
- `.env`: Environment variables for the project (not included in the repository, should be created manually).

## Code Explanation

### Importing Required Libraries

```python
import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import logging
import pandas as pd
from sqlalchemy import create_engine
```

### Loading Environment Variables

```python
load_dotenv()
```

### Function to Execute SQL Queries

```python
def read_sql_query(sql, db_params):
    try:
        DATABASE_URL = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = pd.read_sql_query(sql, conn)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### Configuration and Initialization

```python
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ny_taxi',
    'port': 5432
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-pro')
```

### Functions for Gemini AI Interaction

```python
def get_gemini_response(prompt, question):
    try:
        response = model.generate_content([prompt, question])
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None

def sanitize_sql(sql):
    sql = sql.strip().strip(';')
    return sql
```

### Streamlit App Definition

```python
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

if submit:
    sql_query = get_gemini_response(sql_prompt, question)
    if sql_query:
        sql_query = sanitize_sql(sql_query)
        response = read_sql_query(sql_query, db_params)
        if response is not None and not response.empty:
            st.subheader("The Response is")
            st.write(sql_query)
            formatted_prompt = paraphrase_prompt.format(question=question, result=response.to_string())
            paraphrased_response = get_gemini_response(formatted_prompt, "")
            st.subheader("Paraphrased Response")
            st.write(paraphrased_response)
        else:
            st.write("No data found.")
    else:
        st.write("There was an error generating the SQL query. Please try again.")
```

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. We welcome any improvements, bug fixes, or new features.

## Contact

For any questions or issues, please contact harrati.yassine2002@gmail.com or jaouad.ouchbar@edu.uiz.ac.ma .
