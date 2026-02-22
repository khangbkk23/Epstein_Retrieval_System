import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from typing import List, TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from core.vector_store import VectorStore
from core.embedder import VectorEmbedder

class GraphState(TypedDict):
    question: str
    documents: List[Dict[str, Any]]
    generation: str
    search_attempts: int


class GradeDocuments(BaseModel):
    binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

class AgenticRAGEngine:
    def __init__(self, llm_api_key: str):
        logger.info("Initializing Agentic RAG Engine via LangGraph...")

        self.vector_store = VectorStore()
        self.vector_store.load()
        self.embedder = VectorEmbedder()
        
        self.evaluator_llm = ChatOpenAI(api_key=llm_api_key, model="gpt-4o-mini", temperature=0)
        self.generator_llm = ChatOpenAI(api_key=llm_api_key, model="gpt-4o-mini", temperature=0.3)
        
        # Build the Graph
        self.workflow = self._build_graph()

    def retrieve(self, state: GraphState) -> GraphState:
        logger.info("--- NODE: RETRIEVE")
        question = state["question"]
        attempts = state.get("search_attempts", 0)
        question_vector = self.embedder.embed_batch([question])[0]
        results = self.vector_store.search(question_vector, top_k=5)
        
        documents = [res[0] for res in results]
        
        return {"documents": documents, "question": question, "search_attempts": attempts + 1}

    def grade_documents(self, state: GraphState) -> GraphState:
        logger.info("--- NODE: GRADE DOCUMENTS")
        question = state["question"]
        documents = state["documents"]
        
        # System prompt to force strict evaluation
        system = """You are a strict grader assessing relevance of a retrieved document to a user question. 
        If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. 
        Give a binary score 'yes' or 'no'."""
        
        grade_prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}")
        ])
    
        structured_llm = self.evaluator_llm.with_structured_output(GradeDocuments)
        grader = grade_prompt | structured_llm
        
        filtered_docs = []
        for d in documents:
            doc_text = d.get("text", "")
            score = grader.invoke({"question": question, "document": doc_text})
            
            if score.binary_score == "yes":
                logger.info("Document marked as RELEVANT.")
                filtered_docs.append(d)
            else:
                logger.info("Document marked as IRRELEVANT. Filtering out.")
                
        return {"documents": filtered_docs, "question": question}
    
    def generate(self, state: GraphState) -> GraphState:
        logger.info("--- NODE: GENERATE")
        question = state["question"]
        documents = state["documents"]
        
        context = "\n\n".join([d.get("text", "") for d in documents])
        
        prompt = ChatPromptTemplate.from_template(
            """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know. Keep the answer concise.
            
            Question: {question} 
            Context: {context} 
            Answer:"""
        )
        
        rag_chain = prompt | self.generator_llm
        response = rag_chain.invoke({"context": context, "question": question})
        
        return {"generation": response.content}

    def rewrite_query(self, state: GraphState) -> GraphState:
        logger.info("--- NODE: REWRITE QUERY")
        question = state["question"]
        
        system = """You are a question re-writer that converts an input question to a better version that is optimized 
        for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
        
        re_write_prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "Here is the initial question: \n\n {question} \n Formulate an improved question.")
        ])
        
        question_rewriter = re_write_prompt | self.evaluator_llm
        better_question = question_rewriter.invoke({"question": question})
        
        logger.info(f"Original Query: {question} | Rewritten Query: {better_question.content}")
        return {"question": better_question.content}

    def decide_to_generate(self, state: GraphState) -> str:
        logger.info("--- EVALUATING CONDITIONAL EDGE")
        filtered_documents = state["documents"]
        attempts = state["search_attempts"]
        
        # Prevent infinite loops: Max 2 search attempts
        if not filtered_documents and attempts < 2:
            logger.info("DECISION: All documents irrelevant. Routing to rewrite query.")
            return "rewrite_query"
        elif not filtered_documents and attempts >= 2:
             logger.warning("DECISION: Max attempts reached without relevant docs. Forcing generate to return fallback answer.")
             return "generate"
        else:
            logger.info("DECISION: Relevant documents found. Routing to generate.")
            return "generate"

    def _build_graph(self):
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("grade_documents", self.grade_documents)
        workflow.add_node("generate", self.generate)
        workflow.add_node("rewrite_query", self.rewrite_query)

        # Build graph edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        
        # Conditional branching after grading
        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "rewrite_query": "rewrite_query",
                "generate": "generate",
            }
        )
        
        workflow.add_edge("rewrite_query", "retrieve")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def run(self, question: str) -> str:
        initial_state = {"question": question, "search_attempts": 0}
        
        logger.info(f"Starting Graph execution for question: {question}")
        final_state = self.workflow.invoke(initial_state)
        
        return final_state.get("generation", "Error: No generation produced.")