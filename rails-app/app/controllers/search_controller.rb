require 'httparty'

class SearchController < ApplicationController
  def index
    # Render the main search page
  end

  def search
    query = params[:q] || params[:query]
    
    if query.blank?
      render json: { results: [], message: 'Please enter a search query' }
      return
    end

    begin
      # Connect to MeiliSearch
      meilisearch_url = ENV['MEILISEARCH_URL'] || 'http://meilisearch:7700'
      meilisearch_key = ENV['MEILISEARCH_KEY']
      
      if meilisearch_key.blank?
        render json: { 
          error: 'Configuration error', 
          message: 'MEILISEARCH_KEY environment variable is required',
          results: []
        }, status: 500
        return
      end
      
      # Perform search
      response = HTTParty.post(
        "#{meilisearch_url}/indexes/akutagawa_stories/search",
        headers: {
          'Authorization' => "Bearer #{meilisearch_key}",
          'Content-Type' => 'application/json'
        },
        body: {
          q: query,
          limit: 20
        }.to_json
      )

      if response.success?
        results = response.parsed_response
        render json: {
          results: results['hits'] || [],
          total: results['estimatedTotalHits'] || 0,
          query: query
        }
      else
        render json: { 
          error: 'Search failed', 
          message: response.body,
          results: []
        }, status: 500
      end

    rescue => e
      render json: { 
        error: 'Connection failed', 
        message: e.message,
        results: []
      }, status: 500
    end
  end
end
