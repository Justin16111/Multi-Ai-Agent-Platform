import chromadb

client = chromadb.Client()

memory_collection = client.get_or_create_collection(
    name="chat_memory"
)