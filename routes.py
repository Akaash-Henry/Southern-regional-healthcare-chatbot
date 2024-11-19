from flask import render_template, redirect, url_for, flash, request
from flask import Flask, render_template, request, jsonify
from app import app, db, bcrypt
from app import predict_disease
from app import chat_history
from models.user import User
from forms.forms import RegistrationForm, LoginForm
from models.chat_history import ChatHistory
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    repeat_password = request.form.get('repeat_password')

    # Check if the current password is correct
    if not bcrypt.check_password_hash(current_user.password, current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('profile'))

    # Check if the new passwords match
    if new_password != repeat_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('profile'))

    # Hash the new password and update the user's password in the database
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    current_user.password = hashed_password
    db.session.commit()

    flash('Your password has been updated!', 'success')
    return redirect(url_for('profile'))

# Landing Page Route
@app.route("/", methods=['GET'])
def index():
    return render_template('index.html', title='Index Page')

# Registration Route

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))  # Redirect logged-in users to chat
    
    if request.method == 'POST':
        # Fetch form data from the standard HTML form
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create and save the new user
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))

    # Render the registration template if it's a GET request
    return render_template('register.html', title='Register')

# Login Route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    
    if request.method == 'POST':
        # Fetch the form data
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Query the user from the database
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('chat'))  # Redirect to the chat page
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login')


# Profile Route
@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title='profile', user=current_user)

# Logout Route
@app.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

# Chat Route
@app.route("/chat", methods=['GET', 'POST'])
@login_required
def chat():
    global chat_history 
    if request.method == 'POST':
        user_input = request.form['user_input']
        bot_response = predict_disease(user_input)

        # Save user message to chat history
        user_chat = ChatHistory(user_id=current_user.id, message=user_input)
        db.session.add(user_chat)
        
        # Save bot response to chat history
        bot_chat = ChatHistory(user_id=current_user.id, message=bot_response)
        db.session.add(bot_chat)
        db.session.commit()


        chat_history.append({"user": user_input, "bot": bot_response})
        
        return jsonify(chat_history=chat_history)


    return render_template("chat.html", chat_history=chat_history)
    

