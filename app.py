import re
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import cohere
import pymongo
from scipy.sparse import vstack


app = Flask(__name__)


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['farming_db']
collection = db['queries']


cohere_api_key = '0uMtdMXPqDjrH4VGMgxFRXyJ1yX9frhD4YmNA1vV'
co = cohere.Client(cohere_api_key)

vectorizer = TfidfVectorizer()
X = None
relevant_queries = [] 
query_data_map = {}  


def precompute_tfidf_matrix():
    global X, vectorizer, relevant_queries, query_data_map
    try:
       
        first_documents = collection.find({}).sort('_id', pymongo.ASCENDING).limit(700)
        
        last_documents = collection.find({}).sort('_id', pymongo.DESCENDING).limit(700)

        relevant_queries = []
        query_data_map = {}

        for doc in first_documents:
            query_text = doc.get('QueryText', '')
            crop = doc.get('Crop', '')
            combined_query = f"{crop} {query_text}" if crop else query_text
            relevant_queries.append(combined_query)
            query_data_map[combined_query] = doc  

        for doc in last_documents:
            query_text = doc.get('QueryText', '')
            crop = doc.get('Crop', '')
            combined_query = f"{crop} {query_text}" if crop else query_text
            relevant_queries.append(combined_query)
            query_data_map[combined_query] = doc 


        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(relevant_queries)
        print("TF-IDF matrix precomputed for selected queries!")
    except Exception as e:
        print(f"Error precomputing TF-IDF matrix: {e}")

def update_tfidf_matrix(new_query_text, new_doc):
    global X, vectorizer, relevant_queries, query_data_map
    try:
        crop = new_doc.get('Crop', '')
        combined_query = f"{crop} {new_query_text}" if crop else new_query_text
        
        # Add the new query to the list of relevant queries
        relevant_queries.append(combined_query)
        query_data_map[combined_query] = new_doc
        
        # Vectorize the new query
        new_vector = vectorizer.transform([combined_query])
        
        # Update the TF-IDF matrix by stacking the new query vector
        X = vstack([X, new_vector])
        print("TF-IDF matrix updated with new query!")
    except Exception as e:
        print(f"Error updating TF-IDF matrix: {e}")


# Text cleaning utility
def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'\W', ' ', text).lower()  # Clean and convert to lowercase
    else:
        return str(text).lower()  # Convert non-string types to string and lowercase

# Exact match check for user input
def exact_match_check(user_input):
    cleaned_input = clean_text(user_input)
    for query, doc in query_data_map.items():
        if clean_text(query) == cleaned_input:
            print(f"Exact match found for query: {user_input}")
            return doc  # Return the document if exact match is found
    print(f"No exact match found for query: {user_input}")
    return None

# Word match checking function
def word_match_check(user_input, query_text):
    user_words = set(clean_text(user_input).split())
    query_words = set(clean_text(query_text).split())
    match_count = len(user_words & query_words)
    print(f"Word Match Count: {match_count}")
    return match_count >= 3  # Ensure at least 3 words match

# Find the best match using cosine similarity
def find_best_match(user_input):
    try:
        # Check for exact match first
        exact_match = exact_match_check(user_input)
        if exact_match:
            print(f"Exact match found: {exact_match}")
            return exact_match

        # If no exact match, proceed with cosine similarity
        user_input_cleaned = clean_text(user_input)
        user_vector = vectorizer.transform([user_input_cleaned])
        similarity_scores = cosine_similarity(user_vector, X)
        print(f"Similarity Scores: {similarity_scores}")

        best_match_index = similarity_scores.argmax()
        best_score = similarity_scores[0, best_match_index]
        print(f"Best Match Index: {best_match_index}, Score: {best_score}")

        if best_score > 0.7:  # Adjusted threshold
            best_query = relevant_queries[best_match_index]
            best_doc = query_data_map[best_query]

            # Add logging for word match check
            print(f"Best Query Found: {best_query}")
            if word_match_check(user_input, best_doc.get('QueryText', '')):
                print(f"Returning Best Match with Score: {best_score}")
                return best_doc
            else:
                print(f"Word match failed, rejecting query: {best_query}")

        # No match found, return None
        return None
    except Exception as e:
        print(f"Error finding best match: {e}")
        return None

# Generate response using Cohere API
def get_cohere_response(prompt):
    refined_prompt = (
        f"Please provide a brief response (1-2 sentences or approximately 10-20 words) to the following farming-related question: '{prompt}'. "
        "Be concise and focus on the most relevant information directly answering the question."
    )
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=refined_prompt,
        max_tokens=50
    )
    return response.generations[0].text.strip()

# Add a new query and its response to the database
def add_query_to_db(user_input, cohere_response):
    try:
        cleaned_input = clean_text(user_input)
        new_doc = {
            'Crop': 'UNKNOWN',        # Set to 'UNKNOWN' or relevant crop
            'StateName': 'UNKNOWN',   # Set to 'UNKNOWN' or relevant state
            'QueryText': cleaned_input,  # Clean the input before storing
            'KccAns': cohere_response,
        }
        collection.insert_one(new_doc)
        print("New query and response added to the database.")
        
        # Incrementally update the TF-IDF matrix
        update_tfidf_matrix(cleaned_input, new_doc)
    except Exception as e:
        print(f"Error adding query to database: {e}")

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Handle user queries
@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_input = request.json.get('query')
        print(f"User input: {user_input}")
        
        # Check for an exact match first
        exact_match = exact_match_check(user_input)
        if exact_match:
            print(f"Exact match found: {exact_match}")
            return jsonify({'response': exact_match.get('KccAns', 'No answer found')})
        
        # Find the best match using TF-IDF and cosine similarity
        best_match = find_best_match(user_input)
        print(f"Best match: {best_match}")

        if best_match:
            return jsonify({'response': best_match.get('KccAns', 'No answer found')})
        else:
            # Get response from Cohere if no match above 0.7
            cohere_response = get_cohere_response(user_input)
            add_query_to_db(user_input, cohere_response)  # Add new query and response to DB

            return jsonify({'response': cohere_response})
    except Exception as e:
        print(f"Error in ask route: {e}")
        return jsonify({'response': "An error occurred. Please try again later."})

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Run the Flask app
if __name__ == '__main__':
    # Precompute the TF-IDF matrix before starting the app
    precompute_tfidf_matrix()
    app.run(debug=True)
