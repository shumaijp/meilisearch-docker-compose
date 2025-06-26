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

def fetch_akutagawa_story():
    """Fetch the Akutagawa story from the URL"""
    url = "https://www.aozora.gr.jp/cards/000879/files/92_14545.html"
    
    try:
        response = requests.get(url)
        response.encoding = 'shift_jis'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        main_text = soup.find('div', class_='main_text')
        if not main_text:
            main_text = soup.find('div', {'class': 'honbun'}) or soup.find('div', {'id': 'honbun'})
        
        if main_text:
            lines = []
            for p in main_text.find_all(['p', 'br']):
                if p.name == 'p':
                    text = p.get_text().strip()
                    if text:
                        lines.append(text)
                elif p.name == 'br':
                    if p.next_sibling and isinstance(p.next_sibling, str):
                        text = p.next_sibling.strip()
                        if text:
                            lines.append(text)
            
            if not lines:
                text_content = main_text.get_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            return lines
        else:
            text_content = soup.get_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip() and len(line.strip()) > 10]
            return lines[:100]  # Limit to first 100 meaningful lines
            
    except Exception as e:
        print(f"Error fetching story: {e}")
        return [
            "羅生門の下で、下人が雨やみを待っていた。",
            "広い門の下には、この男のほかに誰もいない。",
            "ただ、所々丹塗の剥げた、大きな円柱に、蟋蟀が一匹とまっている。",
            "羅生門が、朱雀大路にある以上は、この男のほかにも、雨やみを待っている人があってもよさそうなものである。",
            "それが、この男のほかには誰もいない。"
        ]

def load_data_to_meilisearch(client, lines):
    """Load story lines into MeiliSearch"""
    
    index_name = 'akutagawa_stories'
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
    
    print("Fetching Akutagawa story...")
    lines = fetch_akutagawa_story()
    print(f"Fetched {len(lines)} lines")
    
    load_data_to_meilisearch(client, lines)
    
    print("Data loader finished!")

if __name__ == "__main__":
    main()
