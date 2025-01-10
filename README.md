
# RAG Application with Milvus, Ollama, and Hugging Face

This project is a **Retrieval-Augmented Generation (RAG)** application that combines cutting-edge technologies to deliver efficient and secure AI-driven solutions.

## Key Features

1. **Knowledge Retrieval with Milvus**
   - Leverages [Milvus](https://milvus.io/), an open-source vector database, to store and query embeddings for fast and scalable document retrieval.

2. **Language Model via Ollama Client**
   - Integrates the [Ollama Client](https://ollama.ai/) for seamless interaction with a Large Language Model (LLM), generating contextually rich and accurate responses.

3. **Embedding Generation with Hugging Face**
   - Utilizes a Hugging Face embedder for creating high-quality embeddings for document indexing and query understanding.

4. **Secure Authentication with Google OAuth**
   - Ensures secure access by restricting logins to users from a specific company domain using Google OAuth.

5. **Data Management with MySQL**
   - Stores metadata, user sessions, and additional project-related information in a robust relational database.

6. **User-Friendly Interface**
   - A **Streamlit app** provides an intuitive and interactive interface for seamless user interaction.

## Use Cases
- AI-powered document retrieval systems
- Enterprise-level chatbots with secure access
- Knowledge management tools for teams
- Personalized AI assistant applications

## How It Works
1. Users log in via Google OAuth, restricted to a specific company domain.
2. Queries are embedded using Hugging Face and searched against the vector data stored in Milvus.
3. The retrieved context is fed into the Ollama LLM, which generates a relevant response.
4. MySQL manages additional data and user interactions for reliable operations.

## Technology Stack
- **Vector Database:** Milvus for storing and retrieving embeddings
- **Embeddings:** Hugging Face for embedding generation
- **LLM:** Ollama client for advanced language understanding
- **Interface:** Streamlit for an easy-to-use app

