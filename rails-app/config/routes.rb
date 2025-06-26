Rails.application.routes.draw do
  root 'search#index'
  get '/search', to: 'search#search'
  post '/search', to: 'search#search'
end
