import chromadb
import os

DB_PATH = "./chroma_db"
COLLECTION_NAME = "zoom_meeting_docs"

print(f"--- ChromaDB Inspector ---")
print(f"Attempting to connect to database at: {os.path.abspath(DB_PATH)}")
print(f"Looking for collection: '{COLLECTION_NAME}'")
print("-" * 26)

try:
    # Connect to the persistent database
    client = chromadb.PersistentClient(path=DB_PATH)

    # Get the collection
    collection = client.get_collection(name=COLLECTION_NAME)

    # Get the total count of items
    count = collection.count()

    print(f"✅ SUCCESS: Connected to collection.")
    print(f"📊 Total documents in collection: {count}")

    if count > 0:
        print("\n--- Sample of 2 Documents ---")
        # Get a small sample of the items to see what's inside
        sample = collection.get(limit=2, include=["metadatas", "documents"])
        print(sample)
        print("-" * 28)
    else:
        print("\n❌ The collection is EMPTY. No data was ingested.")

except Exception as e:
    print(f"\n❌ ERROR: Could not connect to or read the collection.")
    print(f"   Error details: {e}")
    print(f"   This likely means the database at '{DB_PATH}' doesn't exist or the collection name is wrong.")