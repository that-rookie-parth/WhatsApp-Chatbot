from indexing import index
import openai
import os
from dotenv import load_dotenv
from twilio.rest import Client
from llm import memory, conversation

load_dotenv()
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

# function to provide the gpt with context of the given docs
def get_similiar_docs(query, k=1, score=False):
    if score:
        similar_docs = index.similarity_search_with_score(query, k=k)
    else:
        similar_docs = index.similarity_search(query, k=k)
    return similar_docs

# query refiner func
def query_refiner(conversation, query):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:",
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response["choices"][0]["text"]

# to send message to WhatsApp
def send_message(to: str, message: str) -> None:
    '''
    Send message to a Telegram user.

    Parameters:
        - to(str): sender whatsapp number in this whatsapp:+919558515995 form
        - message(str): text message to send

    Returns:
        - None
    '''

    _ = client.messages.create(
        from_=os.getenv('FROM'),
        body=message,
        to=to
    )

def get_response(prompt: str) -> dict:
    '''
    Call Openai API for text completion

    Parameters:
        - prompt: user query (str)

    Returns:
        - dict
    '''
    try:
        # Get response from Openai
        refined_query = query_refiner(
            memory.load_memory_variables, 
            query=prompt,
        )
        context = get_similiar_docs(refined_query)
        response = conversation.predict(
            input=f"Context:\n {context} \n\n Query: \n{refined_query}"
        )
        return {
            'status': 1,
            # 'response': response['choices'][0]['text']
            'response': response
        }
    except:
        return {
            'status': 0,
            'response': ''
        }