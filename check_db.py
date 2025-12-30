import sqlite3
import json

try:
    db_path = 'chroma_db/chroma.sqlite3'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables in Chroma DB:')
    for table in tables:
        print(f'  - {table[0]}')
        
    # Check if embeddings table exists and query it
    table_names = [table[0] for table in tables]
    if 'embeddings' in table_names:
        cursor.execute('SELECT COUNT(*) FROM embeddings')
        count = cursor.fetchone()[0]
        print(f'Embeddings count: {count}')
        
        if count > 0:
            # First, let's see what columns exist in embeddings table
            cursor.execute("PRAGMA table_info(embeddings)")
            columns = cursor.fetchall()
            print('\nEmbeddings table columns:')
            for col in columns:
                print(f'  - {col[1]} ({col[2]})')
                
            cursor.execute('SELECT * FROM embeddings LIMIT 3')
            rows = cursor.fetchall()
            print('\nSample embeddings (first 3):')
            for i, row in enumerate(rows):
                print(f'  Row {i}: {row}')
                print()
                
            # Check metadata table
            cursor.execute('SELECT * FROM embedding_metadata LIMIT 5')
            meta_rows = cursor.fetchall()
            print('\nSample embedding metadata:')
            for i, row in enumerate(meta_rows):
                print(f'  Row {i}: {row}')
                
            # Look for loan/Mindbowser content in the document field
            # First check document names from embedding_metadata
            cursor.execute("SELECT DISTINCT string_value FROM embedding_metadata WHERE key = 'document_name'")
            doc_names = cursor.fetchall()
            print(f'\nUnique document names in database:')
            for doc in doc_names:
                print(f'  - {doc[0]}')
                
            # Check if any documents contain loan/Mindbowser content
            cursor.execute("SELECT string_value FROM embedding_metadata WHERE key = 'chroma:document' AND (string_value LIKE '%loan%' OR string_value LIKE '%Mindbowser%' OR string_value LIKE '%policy%') LIMIT 10")
            content_matches = cursor.fetchall()
            print(f'\nContent containing loan/Mindbowser/policy: {len(content_matches)}')
            for match in content_matches:
                print(f'  Content: {str(match[0])[:200]}...')
                print()
                        
    else:
        print('No embeddings table found')
        
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')