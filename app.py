import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import logging
import pandas as pd
from sqlalchemy import create_engine

# Load all the environment variables
load_dotenv()

def read_sql_query(sql, db_params):
    try:
        # Créer l'URL de la base de données
        DATABASE_URL = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

        # Créer une connexion SQLAlchemy Engine
        engine = create_engine(DATABASE_URL)
        
        # Utiliser pandas pour exécuter la requête SQL et lire les résultats dans un DataFrame
        with engine.connect() as conn:
            result = pd.read_sql_query(sql, conn)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

# Exemple d'utilisation
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ny_taxi',
    'port': 5432
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Google Gemini Model
model = genai.GenerativeModel('gemini-pro')

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(prompt, question):
    try:
        response = model.generate_content([prompt, question])
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return None

# Function to sanitize the generated SQL query
def sanitize_sql(sql):
    # Basic sanitization to ensure there are no malicious inputs
    # This can be enhanced based on specific requirements
    sql = sql.strip().strip(';')
    return sql

# Define your prompt for SQL generation
sql_prompt = """
You are an expert in converting English questions to SQL query!
The SQL database has the name players and has the following columns - 
player_id (INTEGER PRIMARY KEY AUTOINCREMENT), first_name (TEXT), last_name (TEXT), 
position (TEXT), team (TEXT), age (INTEGER), nationality (TEXT).

For example,
Example 1 - How many players are there?, 
the SQL command will be something like this: SELECT COUNT(*) FROM players;
Example 2 - List all players in the team 'Barcelona', 
the SQL command will be something like this: SELECT * FROM players WHERE team='Barcelona';

Guidelines:
1. Ensure the SQL code is syntactically correct and does not include delimiters like `;`.
2. Avoid SQL keywords or delimiters in the output.
3. Handle different variations of questions accurately.
4. The SQL code should be valid, executable, and not contain unnecessary delimiters.

Schema:
- Table: players
  Columns: player_id INTEGER PRIMARY KEY AUTOINCREMENT,
           first_name TEXT,
           last_name TEXT,
           position TEXT,
           team TEXT,
           age INTEGER,
           nationality TEXT
"""

# Define your prompt for paraphrasing
paraphrase_prompt = """
You are an expert in paraphrasing responses.
Given the following question and its corresponding result, provide a well-formulated response that summarizes the information accurately.

Question: {question}
Result: {result}

Paraphrased Response:
"""

# Streamlit App
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question = st.text_input("Input: ", key="input")

submit = st.button("Ask the question")

if submit:
    # Reformuler la question

    # Générer la requête SQL à partir de la question reformulée
    sql_query = get_gemini_response(sql_prompt, question)
    if sql_query:
        sql_query = sanitize_sql(sql_query)
        
        response = read_sql_query(sql_query, db_params)
        if response is not None and not response.empty:
            st.subheader("The Response is")
            st.write(sql_query)
            
            # Paraphraser la réponse
            formatted_prompt = paraphrase_prompt.format(question=question, result=response.to_string())

            paraphrased_response = get_gemini_response(formatted_prompt, "")
            st.subheader("Paraphrased Response")
            st.write(paraphrased_response)
        else:
            sql_prompt=''
            sql_query = get_gemini_response(sql_prompt, question)
            st.write(sql_query)
    else:
        st.write("There was an error generating the SQL query. Please try again.")
