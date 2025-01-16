import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from openai import AzureOpenAI
import datetime
import logging

# Load environment variables
load_dotenv()

# Validate environment variables
required_env_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_env_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_env_vars)}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Azure OpenAI Configuration
try:
    openai_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    # Deployment name for the model
    DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    logger.info("Azure OpenAI client configured successfully.")
except Exception as e:
    logger.error(f"Azure OpenAI Configuration Error: {e}")
    DEPLOYMENT_NAME = None

class HRChatbot:
    def __init__(self, openai_client):
        self.client = openai_client
        self.candidate_data = {}
    
    def validate_input(self, field, value):
        """
        Validate input based on field type
        """
        if not value:
            return False
        
        if field == 'mobile':
            # Indian mobile number validation
            import re
            return re.match(r'^[6-9]\d{9}$', str(value)) is not None
        
        elif field == 'email':
            # Email validation
            import re
            return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(value)) is not None
        
        elif field == 'percentage':
            try:
                percentage = float(value)
                return 0 <= percentage <= 100
            except ValueError:
                return False
        
        return True
    
    def evaluate_candidate(self, conversation_history):
        """
        Evaluate candidate using Azure OpenAI
        """
        try:
            # Prepare detailed evaluation prompt
            evaluation_prompt = f"""
            Comprehensive Candidate Evaluation:

            Conversation Context: {conversation_history}

            Evaluation Criteria:
            1. Communication Skills (25%):
               - Clarity of expression
               - Articulation
               - Professional communication

            2. Future Vision (20%):
               - Career goals
               - Ambition
               - Strategic thinking

            3. Conflict Resolution (30%):
               - Problem-solving approach
               - Handling workplace challenges
               - Interpersonal skills

            4. Personality Fit (25%):
               - Cultural alignment
               - Team collaboration
               - Adaptability

            Provide a detailed assessment with:
            - Score for each criterion (0-10)
            - Specific justifications
            - Overall weighted score
            - Final recommendation
            """
            
            # Call Azure OpenAI with the evaluation prompt
            response = self.client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional conducting a comprehensive candidate evaluation."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Candidate Evaluation Error: {e}")
            return f"Evaluation could not be completed. Error: {str(e)}"
    
    def check_time_constraints(self):
        """
        Check interview time constraints
        """
        current_time = datetime.datetime(2025, 1, 16, 17, 31, 17)
        return current_time.hour < 18

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_application', methods=['POST'])
def submit_application():
    # Validate OpenAI client is configured
    if not DEPLOYMENT_NAME:
        return jsonify({'error': 'OpenAI client not configured'}), 500
    
    # Initialize chatbot with OpenAI client
    chatbot = HRChatbot(openai_client)
    
    # Collect form data
    candidate_data = {
        'name': request.form.get('name'),
        'mobile': request.form.get('mobile'),
        'email': request.form.get('email'),
        'post_applied': request.form.get('post_applied'),
        'tenth_marks': request.form.get('tenth_marks'),
        'parents_income': request.form.get('parents_income'),
        'category': request.form.get('category'),
        'religion': request.form.get('religion'),
        'interests': request.form.get('interests'),
        'future_vision': request.form.get('future_vision'),
        'additional_info': request.form.get('additional_info')
    }
    
    # Validate inputs
    for field, value in candidate_data.items():
        if not chatbot.validate_input(field, value):
            return jsonify({'error': f'Invalid input for {field}'}), 400
    
    # Check time constraints
    if not chatbot.check_time_constraints():
        return jsonify({'error': 'Interview time constraint violated'}), 400
    
    # Simulate evaluation (in real scenario, this would use actual interview data)
    conversation_history = request.form.get('conversation_history', '')
    evaluation = chatbot.evaluate_candidate(conversation_history)
    
    return jsonify({
        'candidate_data': candidate_data,
        'evaluation': evaluation
    })

# Error Handling
@app.errorhandler(500)
def handle_500(error):
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
