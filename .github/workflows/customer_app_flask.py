"""
QueueEase - Customer App (Flask)
Run with: python customer_app_flask.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import json
from datetime import datetime
import random
import secrets


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration - easily modify settings here"""
    SECRET_KEY = secrets.token_hex(16)
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'
    
    # Validation rules
    MIN_PHONE_LENGTH = 10
    MIN_NAME_LENGTH = 2
    
    # Queue simulation
    POSITION_UPDATE_PROBABILITY = 0.7  # 70% chance to move forward in queue


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Centralized error messages for easy modification"""
    INVALID_PHONE = 'Invalid phone number'
    INVALID_NAME = f'Name must be at least {Config.MIN_NAME_LENGTH} characters'
    PHONE_EXISTS = 'Phone number already registered'
    PHONE_NOT_FOUND = 'Phone number not found. Please register first.'
    NOT_AUTHENTICATED = 'Not authenticated'
    CATEGORY_NOT_FOUND = 'Category not found'
    INVALID_CATEGORY = 'Invalid category'
    PLACE_NOT_FOUND = 'Place not found'


# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


# ============================================================================
# DATA STORAGE (In-Memory Database)
# ============================================================================

users_db = {}  # Store users: {phone: {name, registered_at}}
queue_data_per_user = {}  # Store queue data per user: {phone: {current_queue, history}}


# ============================================================================
# STATIC DATA - RESTAURANTS
# ============================================================================

restaurants = [
    {
        'id': '1',
        'name': 'Bella Italia',
        'cuisine': 'Italian',
        'queue_size': 8,
        'wait_time': 25,
        'rating': 4.5,
        'distance': '0.5 km',
    },
    {
        'id': '2',
        'name': 'Sushi Palace',
        'cuisine': 'Japanese',
        'queue_size': 12,
        'wait_time': 40,
        'rating': 4.7,
        'distance': '1.2 km',
    },
    {
        'id': '3',
        'name': 'The Burger Joint',
        'cuisine': 'American',
        'queue_size': 5,
        'wait_time': 15,
        'rating': 4.3,
        'distance': '0.8 km',
    },
    {
        'id': '4',
        'name': 'Spice Garden',
        'cuisine': 'Indian',
        'queue_size': 15,
        'wait_time': 50,
        'rating': 4.6,
        'distance': '2.1 km',
    },
    {
        'id': '5',
        'name': 'Taco Fiesta',
        'cuisine': 'Mexican',
        'queue_size': 3,
        'wait_time': 10,
        'rating': 4.4,
        'distance': '0.3 km',
    },
    {
        'id': '6',
        'name': 'Dragon Wok',
        'cuisine': 'Chinese',
        'queue_size': 9,
        'wait_time': 30,
        'rating': 4.5,
        'distance': '1.5 km',
    }
]


# ============================================================================
# STATIC DATA - CATEGORIES
# ============================================================================

categories = [
    {
        'id': 'restaurants',
        'name': 'Restaurants',
        'icon': '🍽️',
        'description': 'Book your table',
        'color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
        'id': 'banks',
        'name': 'Banks',
        'icon': '🏦',
        'description': 'Banking services',
        'color': 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
    },
    {
        'id': 'government',
        'name': 'Government',
        'icon': '🏛️',
        'description': 'Public services',
        'color': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
    }
]


# ============================================================================
# STATIC DATA - BANKS
# ============================================================================

banks = [
    {
        'id': 'b1',
        'name': 'National Bank',
        'type': 'Commercial Bank',
        'queue_size': 15,
        'wait_time': 35,
        'rating': 4.2,
        'distance': '0.7 km',
        'services': 'Account opening, Loans, Transfers'
    },
    {
        'id': 'b2',
        'name': 'City Credit Union',
        'type': 'Credit Union',
        'queue_size': 8,
        'wait_time': 20,
        'rating': 4.5,
        'distance': '1.1 km',
        'services': 'Savings, Credit cards, Mortgages'
    },
    {
        'id': 'b3',
        'name': 'Federal Savings',
        'type': 'Savings Bank',
        'queue_size': 12,
        'wait_time': 28,
        'rating': 4.3,
        'distance': '0.4 km',
        'services': 'Deposits, Withdrawals, Statements'
    },
    {
        'id': 'b4',
        'name': 'Trust Bank',
        'type': 'Investment Bank',
        'queue_size': 6,
        'wait_time': 15,
        'rating': 4.6,
        'distance': '1.8 km',
        'services': 'Investment, Trading, Advisory'
    }
]


# ============================================================================
# STATIC DATA - GOVERNMENT SERVICES
# ============================================================================

government_services = [
    {
        'id': 'g1',
        'name': 'DMV Office',
        'type': 'Motor Vehicles',
        'queue_size': 25,
        'wait_time': 60,
        'rating': 3.8,
        'distance': '2.5 km',
        'services': 'License renewal, Registration, ID cards'
    },
    {
        'id': 'g2',
        'name': 'Post Office',
        'type': 'Postal Services',
        'queue_size': 10,
        'wait_time': 25,
        'rating': 4.1,
        'distance': '0.9 km',
        'services': 'Mail, Packages, Stamps'
    },
    {
        'id': 'g3',
        'name': 'City Hall',
        'type': 'Municipal Services',
        'queue_size': 18,
        'wait_time': 45,
        'rating': 3.9,
        'distance': '1.3 km',
        'services': 'Permits, Licenses, Records'
    },
    {
        'id': 'g4',
        'name': 'Tax Office',
        'type': 'Revenue Services',
        'queue_size': 20,
        'wait_time': 50,
        'rating': 3.7,
        'distance': '1.6 km',
        'services': 'Tax filing, Payments, Consultations'
    },
    {
        'id': 'g5',
        'name': 'Social Services',
        'type': 'Welfare Office',
        'queue_size': 22,
        'wait_time': 55,
        'rating': 4.0,
        'distance': '2.0 km',
        'services': 'Benefits, Support, Applications'
    }
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_queue_data(phone):
    """Get or create queue data for a user"""
    if phone not in queue_data_per_user:
        queue_data_per_user[phone] = {
            'current_queue': None,
            'history': []
        }
    return queue_data_per_user[phone]


def get_place_by_category(place_id, category):
    """Retrieve a place by ID from the specified category"""
    if category == 'restaurants':
        return next((r for r in restaurants if r['id'] == place_id), None)
    elif category == 'banks':
        return next((b for b in banks if b['id'] == place_id), None)
    elif category == 'government':
        return next((g for g in government_services if g['id'] == place_id), None)
    return None


def validate_phone(phone):
    """Validate phone number format"""
    return phone and len(phone) >= Config.MIN_PHONE_LENGTH


def validate_name(name):
    """Validate name format"""
    return name and len(name) >= Config.MIN_NAME_LENGTH


# ============================================================================
# ROUTES - PAGE RENDERING
# ============================================================================

@app.route('/')
def index():
    """Main application page - requires authentication"""
    if 'phone' not in session:
        return redirect(url_for('login'))
    return render_template('customer_index.html')


@app.route('/login')
def login():
    """Login/Registration page"""
    if 'phone' in session:
        return redirect(url_for('index'))
    return render_template('login.html')


# ============================================================================
# API ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    phone = data.get('phone', '').strip()
    name = data.get('name', '').strip()
    
    # Validate phone
    if not validate_phone(phone):
        return jsonify({'error': ErrorMessages.INVALID_PHONE}), 400
    
    # Validate name
    if not validate_name(name):
        return jsonify({'error': ErrorMessages.INVALID_NAME}), 400
    
    # Check if phone already exists
    if phone in users_db:
        return jsonify({'error': ErrorMessages.PHONE_EXISTS}), 400
    
    # Create user
    users_db[phone] = {
        'name': name,
        'registered_at': datetime.now().isoformat()
    }
    
    # Log user in
    session['phone'] = phone
    return jsonify({'success': True, 'message': 'Registration successful'})


@app.route('/api/login', methods=['POST'])
def do_login():
    """Login existing user"""
    data = request.json
    phone = data.get('phone', '').strip()
    
    # Check if user exists
    if not phone or phone not in users_db:
        return jsonify({'error': ErrorMessages.PHONE_NOT_FOUND}), 404
    
    # Log user in
    session['phone'] = phone
    return jsonify({'success': True, 'user': users_db[phone]})


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout current user"""
    session.pop('phone', None)
    return jsonify({'success': True})


@app.route('/api/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if 'phone' in session:
        return jsonify({
            'authenticated': True,
            'user': users_db[session['phone']]
        })
    return jsonify({'authenticated': False})


# ============================================================================
# API ROUTES - DATA RETRIEVAL
# ============================================================================

@app.route('/api/categories')
def get_categories():
    """Get all available categories"""
    return jsonify(categories)


@app.route('/api/restaurants')
def get_restaurants():
    """Get all restaurants"""
    return jsonify(restaurants)


@app.route('/api/banks')
def get_banks():
    """Get all banks"""
    return jsonify(banks)


@app.route('/api/government')
def get_government():
    """Get all government services"""
    return jsonify(government_services)


@app.route('/api/places/<category>')
def get_places_by_category(category):
    """Get all places for a specific category"""
    if category == 'restaurants':
        return jsonify(restaurants)
    elif category == 'banks':
        return jsonify(banks)
    elif category == 'government':
        return jsonify(government_services)
    else:
        return jsonify({'error': ErrorMessages.CATEGORY_NOT_FOUND}), 404


# ============================================================================
# API ROUTES - QUEUE MANAGEMENT
# ============================================================================

@app.route('/api/join-queue', methods=['POST'])
def join_queue():
    """Join a queue at a specific place"""
    # Check authentication
    if 'phone' not in session:
        return jsonify({'error': ErrorMessages.NOT_AUTHENTICATED}), 401
    
    user_data = get_user_queue_data(session['phone'])
    
    # Get request data
    data = request.json
    place_id = data.get('restaurant_id')  # keeping same key for compatibility
    category = data.get('category', 'restaurants')
    
    # Find the place
    place = get_place_by_category(place_id, category)
    
    if not place:
        return jsonify({'error': ErrorMessages.PLACE_NOT_FOUND}), 404
    
    # Create queue entry
    user_data['current_queue'] = {
        'place_name': place['name'],
        'place_id': place_id,
        'category': category,
        'position': place['queue_size'] + 1,
        'total_in_queue': place['queue_size'] + 1,
        'joined_at': datetime.now().isoformat(),
        'estimated_wait': place['wait_time']
    }
    
    return jsonify(user_data['current_queue'])


@app.route('/api/current-queue')
def get_current_queue():
    """Get user's current queue status"""
    # Check authentication
    if 'phone' not in session:
        return jsonify({'error': ErrorMessages.NOT_AUTHENTICATED}), 401
    
    user_data = get_user_queue_data(session['phone'])
    return jsonify(user_data['current_queue'])


@app.route('/api/leave-queue', methods=['POST'])
def leave_queue():
    """Leave the current queue"""
    # Check authentication
    if 'phone' not in session:
        return jsonify({'error': ErrorMessages.NOT_AUTHENTICATED}), 401
    
    user_data = get_user_queue_data(session['phone'])
    
    # Move to history if in queue
    if user_data['current_queue']:
        entry = user_data['current_queue'].copy()
        entry['left_at'] = datetime.now().isoformat()
        entry['status'] = 'Left'
        user_data['history'].append(entry)
        user_data['current_queue'] = None
    
    return jsonify({'success': True})


@app.route('/api/update-position', methods=['POST'])
def update_position():
    """Update queue position (simulate queue movement)"""
    # Check authentication
    if 'phone' not in session:
        return jsonify({'error': ErrorMessages.NOT_AUTHENTICATED}), 401
    
    user_data = get_user_queue_data(session['phone'])
    
    # Move forward in queue with configured probability
    if user_data['current_queue'] and user_data['current_queue']['position'] > 1:
        if random.random() < Config.POSITION_UPDATE_PROBABILITY:
            user_data['current_queue']['position'] -= 1
    
    return jsonify(user_data['current_queue'])


@app.route('/api/history')
def get_history():
    """Get user's queue history"""
    # Check authentication
    if 'phone' not in session:
        return jsonify({'error': ErrorMessages.NOT_AUTHENTICATED}), 401
    
    user_data = get_user_queue_data(session['phone'])
    return jsonify(user_data['history'])


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        port=Config.PORT,
        host=Config.HOST
    )