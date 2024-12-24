from flask import Flask, request, render_template, jsonify
import os
from langchain_community.tools import TavilySearchResults
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set up the API keys
if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initialize tools
tool = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Provide a concise, clear response that formats the given {url} and {text} in a readable, human-friendly manner. Ensure no false information is generated. Use URLs to cite sources when applicable.",
        ),
    ]
)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
    user_query = request.form.get('query')
    try:
        response = tool.invoke({"query": user_query})
        urls = [entry['url'] for entry in response]
        texts = [entry['content'] for entry in response]

        chain = prompt | llm
        output = chain.invoke({"url": urls, "text": texts})
        return jsonify({"result": output.content})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
