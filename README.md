# MeiliSearch Docker Compose Environment

A complete Docker Compose environment with MeiliSearch, Ruby on Rails webapp, and data loader for searching story text.

## Components

1. **MeiliSearch Container** - Search engine running on port 7700
2. **Ruby on Rails Webapp** - Web interface with Vue.js frontend on port 3000  
3. **Data Loader** - Python script that fetches and indexes story text from Aozora Bunko

## Quick Start

1. Clone this repository
2. Copy the environment file and set your keys:
   ```bash
   cp .env.example .env
   # Edit .env and set secure values for the keys
   ```
3. Start the environment:
   ```bash
   docker-compose up
   ```
4. Visit http://localhost:3000 to use the search interface

## Features

- Bilingual search interface (Japanese/English)
- Full-text search of story text
- Responsive Vue.js frontend
- Automatic data loading from Aozora Bunko
- Docker Compose orchestration

## Data Source

The data loader fetches text from: https://www.aozora.gr.jp/cards/000879/files/92_14545.html

## Environment Variables

See `.env.example` for required environment variables. You must set secure values for:
- `MEILI_MASTER_KEY` - MeiliSearch master key
- `MEILISEARCH_KEY` - API key for accessing MeiliSearch

## Development

The Rails app includes hot reloading and the data loader will automatically populate the search index on startup.
