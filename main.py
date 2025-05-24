from fastapi import FastAPI, Request
from pydantic import BaseModel
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from fastapi.middleware.cors import CORSMiddleware
#from langchain.chat_models import ChatOpenAI  # or your preferred model

from langchain_google_genai import GoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains import create_sql_query_chain

# Initialize components
load_dotenv()

#llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=os.environ["GOOGLE_API_KEY"])
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.environ["GOOGLE_API_KEY"])

#DB connection established
db_user = "postgres"         # Replace with your PostgreSQL username
db_password = "pgsql123" # Replace with your PostgreSQL password
db_host = "localhost"
db_port = "5432"             # Default PostgreSQL port
db_name = "retail_sales_db"

# PostgreSQL connection string using psycopg2
db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

print("Database connection established!")

#Convert question to SQL query
from langchain.chains import create_sql_query_chain

chain = create_sql_query_chain(llm, db)
response = chain.invoke({"question": "How many customers are there"})

# Example: extract just the SQL part from the response
# This works if the response contains 'SQLQuery: ...'
if "SQLQuery:" in response:
    cleaned_query = response.split("SQLQuery:")[-1].strip()
else:
    cleaned_query = response.strip()  # fallback if formatting is different

print("Cleaned query:\n", cleaned_query)
result = db.run(cleaned_query)
print("Result:", result)

chain = create_sql_query_chain(llm, db)

# def execute_query(question):
#     try:
#         # Generate SQL query from question
#         response = chain.invoke({"question": question})
#         print(response)
#         print("###################################################")

#         # Extract SQL query part from response
#         if "SQLQuery:" in response:
#             cleaned_query = response.split("SQLQuery:")[-1].strip()
#         else:
#             cleaned_query = response.strip()
        
#         print(cleaned_query)
#         print("###################################################")        

#         # Execute the cleaned query
#         result = db.run(cleaned_query)
#         print("###################################################")        

#         # Display the result
#         print(result)
#     except ProgrammingError as e:
#         print(f"An error occurred: {e}")


# q1 = "How many unique customers are there for each product category"
# execute_query(q1)



app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_sql(request: QueryRequest):
    try:
        response = chain.invoke({"question": request.question})
        if "SQLQuery:" in response:
            cleaned_query = response.split("SQLQuery:")[-1].strip()
        else:
            cleaned_query = response.strip()

        result = db.run(cleaned_query)
        return {"query": cleaned_query, "result": result}
    except ProgrammingError as e:
        return {"error": str(e)}




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
