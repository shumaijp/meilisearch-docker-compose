import requests
import time
import os
from bs4 import BeautifulSoup
import meilisearch

def wait_for_meilisearch():
    """Wait for MeiliSearch to be ready"""
    url = os.getenv('MEILISEARCH_URL', 'http://meilisearch:7700')
    key = os.getenv('MEILISEARCH_KEY')
    if not key:
        raise Exception("MEILISEARCH_KEY environment variable is required")
    
    for i in range(30):
        try:
            client = meilisearch.Client(url, key)
            client.health()
            print("MeiliSearch is ready!")
            return client
        except Exception as e:
            print(f"Waiting for MeiliSearch... ({i+1}/30)")
            time.sleep(2)
    
    raise Exception("MeiliSearch not available after 60 seconds")

def fetch_alice_story():
    """Fetch Alice in Wonderland from Aozora Bunko"""
    url = "https://www.aozora.gr.jp/cards/001393/files/57320_57905.html"
    
    try:
        response = requests.get(url)
        response.encoding = 'shift_jis'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        main_text = soup.find('div', class_='main_text')
        if not main_text:
            main_text = soup.find('div', {'class': 'honbun'}) or soup.find('div', {'id': 'honbun'})
        
        if main_text and hasattr(main_text, 'find_all'):
            lines = []
            for p in main_text.find_all('p'):
                text = p.get_text().strip()
                if text and len(text) > 10:  # Only meaningful lines
                    lines.append(text)
            
            if not lines:
                text_content = main_text.get_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip() and len(line.strip()) > 10]
            
            return lines[:50]  # Limit to first 50 lines
        else:
            return [
                "Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do.",
                "Once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it.",
                "And what is the use of a book, thought Alice, without pictures or conversations?",
                "So she was considering in her own mind, as well as she could, for the hot day made her feel very sleepy and stupid.",
                "Whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies.",
                "When suddenly a White Rabbit with pink eyes ran close by her.",
                "There was nothing so very remarkable in that; nor did Alice think it so very much out of the way to hear the Rabbit say to itself.",
                "Oh dear! Oh dear! I shall be late! But when the Rabbit actually took a watch out of its waistcoat-pocket.",
                "And looked at it, and then hurried on, Alice started to her feet, for it flashed across her mind.",
                "That she had never before seen a rabbit with either a waistcoat-pocket, or a watch to take out of it.",
                "And burning with curiosity, she ran across the field after it, and fortunately was just in time to see it pop down a large rabbit-hole under the hedge.",
                "In another moment down went Alice after it, never once considering how in the world she was to get out again.",
                "The rabbit-hole went straight on like a tunnel for some way, and then dipped suddenly down.",
                "So suddenly that Alice had not a moment to think about stopping herself before she found herself falling down a very deep well.",
                "Either the well was very deep, or she fell very slowly, for she had plenty of time as she fell to look about her and to wonder what was going to happen next."
            ]
            
    except Exception as e:
        print(f"Error fetching Alice story: {e}")
        return [
            "Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do.",
            "Once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it.",
            "And what is the use of a book, thought Alice, without pictures or conversations?",
            "So she was considering in her own mind, as well as she could, for the hot day made her feel very sleepy and stupid.",
            "Whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies.",
            "When suddenly a White Rabbit with pink eyes ran close by her.",
            "There was nothing so very remarkable in that; nor did Alice think it so very much out of the way to hear the Rabbit say to itself.",
            "Oh dear! Oh dear! I shall be late! But when the Rabbit actually took a watch out of its waistcoat-pocket.",
            "And looked at it, and then hurried on, Alice started to her feet, for it flashed across her mind.",
            "That she had never before seen a rabbit with either a waistcoat-pocket, or a watch to take out of it.",
            "And burning with curiosity, she ran across the field after it, and fortunately was just in time to see it pop down a large rabbit-hole under the hedge.",
            "In another moment down went Alice after it, never once considering how in the world she was to get out again.",
            "The rabbit-hole went straight on like a tunnel for some way, and then dipped suddenly down.",
            "So suddenly that Alice had not a moment to think about stopping herself before she found herself falling down a very deep well.",
            "Either the well was very deep, or she fell very slowly, for she had plenty of time as she fell to look about her and to wonder what was going to happen next."
        ]

def load_data_to_meilisearch(client, lines):
    """Load story lines into MeiliSearch"""
    
    index_name = 'alice_stories'
    index = client.index(index_name)
    
    documents = []
    for i, line in enumerate(lines):
        if line.strip():  # Only add non-empty lines
            documents.append({
                'id': i + 1,
                'text': line.strip(),
                'line_number': i + 1
            })
    
    print(f"Loading {len(documents)} lines into MeiliSearch...")
    
    task = index.add_documents(documents)
    print(f"Documents added. Task ID: {task.task_uid}")
    
    index.update_searchable_attributes(['text'])
    
    index.update_displayed_attributes(['id', 'text', 'line_number'])
    
    print("Data loading completed!")

def main():
    print("Starting data loader...")
    
    client = wait_for_meilisearch()
    
    print("Fetching Alice in Wonderland story...")
    lines = fetch_alice_story()
    print(f"Fetched {len(lines)} lines")
    
    load_data_to_meilisearch(client, lines)
    
    print("Data loader finished!")

if __name__ == "__main__":
    main()
