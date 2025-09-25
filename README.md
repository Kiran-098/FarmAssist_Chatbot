# FarmAssist_Chatbot
🌾 FarmAssist Chatbot

FarmAssist is a farming query solver chatbot designed to help farmers and agricultural students by providing crop-related solutions and weather-based recommendations.
It uses a combination of Flask (Python), MongoDB, scikit-learn, and Cohere API to answer queries efficiently and store new knowledge dynamically.

🚀 Features

✅ Chatbot for Farming Queries – Ask about crops, irrigation, pesticides, or weather conditions.
✅ MongoDB Database – Stores crop data in a structured JSON format.
✅ Self-Learning Mechanism – New queries and answers are saved for future reference.
✅ Keyword & Similarity Matching – Efficient retrieval using keyword filtering + cosine similarity.
✅ Weather-aware Recommendations – Suggests crops and practices based on weather.
✅ Cohere API Integration – Provides fallback answers when the database doesn’t have an entry.
✅ Web-based Interface – Simple frontend using HTML & CSS, backend powered by Flask.

🛠️ Tech Stack

Backend: Python (Flask)
Database: MongoDB (Compass for manual data entry)
ML/AI: scikit-learn (cosine similarity), Cohere API (fallback)
Frontend: HTML, CSS (single-page chatbot UI)
Deployment: Localhost (Flask)

🧑‍🌾 Usage

Enter a farming-related query, e.g.:
"What is the ideal temperature for rice?"
"Best irrigation method for wheat?
"Optimal rainfall for maize?"

The chatbot will:
Search in MongoDB using keywords + similarity matching.
If no relevant answer is found, query Cohere API.
Save new queries + answers to the database for future use.


License
This project is developed for educational purposes as part of a college project.
Feel free to use, modify, and improve upon it.

