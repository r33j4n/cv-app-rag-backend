import argparse
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.vectorstores import Chroma
from get_model import get_bedrock_model
from get_embedding import get_embedding_function

CHROMA_DB_PATH = "database"

PROMPT_TEMPLATE = """
Answer the question based only on the following context don't exceed the context:

{context}

---

Answer the following question based on the above context: {question}
"""


def query_rag(query_text: str):
    """
    Queries the RAG system with the input text and generates a response.

    Args:
        query_text (str): The input text to query the system.

    Returns:
        str: The response generated by the RAG system.
    """
    # Configure the Database
    embedding_function = get_embedding_function()

    # Initialize Chroma database
    db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embedding_function)

    # Search the Database
    results = db.similarity_search_with_score(query_text, k=5)
    print(results)

    # Extract the context text from search results
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    # Generate a prompt template
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    # Populate the prompt template with context and question
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Initialize the Ollama model
    model = get_bedrock_model()

    # Get the response from the Ollama model based on prompt
    response_text = model.invoke(prompt)

    # Extract sources from search results
    sources = [doc.metadata.get("id", None) for doc, _score in results]

    # Format the response with sources
    formatted_response = f"Response: {response_text}\nSources: {sources}"

    # Return response_text
    return response_text


# print(query_rag("What is the price for the Mac Book 2017"))
