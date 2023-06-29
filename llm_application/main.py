import streamlit as st
from langchain import OpenAI, PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
import qdrant_client
from langchain.schema import Document


template = """You should act as a legal advisor. Be very detailed in your answers.
Also, always display numerical values as they are in the source. When it makes sense, use a bullet point list to display data. T

QUESTION: {question}
=========
{summaries}
=========
FINAL ANSWER IN English:"""

embeddings = OpenAIEmbeddings()


@st.cache_resource
def get_qdrant_client():
    return qdrant_client.QdrantClient(host="localhost", grpc_port=6334, prefer_grpc=True)

@st.cache_resource
def get_qa():
    llm = OpenAI(temperature=0.5, model_name="gpt-3.5-turbo")

       
    prompt = PromptTemplate(
        input_variables=["question", "summaries"],
        template=template,
    )

    qa_chain = load_qa_chain(llm, chain_type="stuff")
    return qa_chain

def main():
    db = get_qdrant_client()
    qa_chain = get_qa()
    st.title("Brønnøysundregisteret Question App")
    
    query = st.text_area("Enter your question here:")
    source = ''
    answer = ''
    if st.button("Submit"):
        query_embedding = embeddings.embed_query(query)
        result = db.search(
            collection_name="brreg",
            query_vector=query_embedding,
            limit=5,
            with_payload=True,
            score_threshold=0.75, #Return only documents with a score of higher than 0.75
        )        

        docs = list(map(lambda x: Document(page_content=x.payload['page_content'], metadata=x.payload['metadata']), result))
        st.markdown(f"#### Sources:")
        sources = list(set(map(lambda x: x.metadata['path'], docs)))
        for s in sources:
            st.markdown(f"##### {s}")

        qa_response = qa_chain.run(input_documents=docs, question=query)        
        st.markdown(f"#### QA Answer:")
        st.markdown(f"##### {qa_response}")

        st.divider()
        

if __name__ == "__main__":
    main()