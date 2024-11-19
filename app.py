
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import joblib

app = Flask(__name__)

# Load the self-contained model
model_data = joblib.load('self_contained_model.pkl')

# Extract components from the model
vectorizer = model_data['vectorizer']
svm_model = model_data['svm_model']
disease_symptoms_df = model_data['disease_symptoms_df']

# Chat history to be retained
chat_history = []

def predict_disease(new_symptom):
    # Vectorize the input symptom
    symptom_vec = vectorizer.transform([new_symptom])

    # Make prediction using the SVM model
    prediction = svm_model.predict(symptom_vec)[0]

    # Look up the response for the predicted disease
    if prediction in disease_symptoms_df['disease'].values:
        response = disease_symptoms_df[disease_symptoms_df['disease'] == prediction]['response'].values[0]
    else:
        response = "I'm not sure what you might have. Please consult a doctor for a proper diagnosis."

    return response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from models.user import User
from routes import routes

if __name__ == '__main__':
    app.run(debug=True)
