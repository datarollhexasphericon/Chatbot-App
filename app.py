from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
import os
from dotenv import load_dotenv
from forms import ChatForm
from datetime import datetime
from completions_model import get_system_reply


# Load environment variables from a .env file
load_dotenv()

# Create a Flask app
app = Flask(__name__)
# Set secret key for session management and other config settings
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Initialize Flask-Bootstrap extension
Bootstrap5(app)

# Create database base class
class Base(DeclarativeBase):
    pass
# Configure the database URI from environment variables or use a default SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///chatbot.db")
# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Create a table to store user-bot communications
class Communications(db.Model):
    __tablename__ = "chatbot_interactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    time: Mapped[str] = mapped_column(String(20), nullable=False)
    messagetype: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(900), nullable=False)

# Drop and recreate the database schema on startup
with app.app_context():
    db.drop_all()
    db.create_all()

# Add an initial bot message to the database
initial_message = Communications(
    time=datetime.now().strftime('%H:%M'),
    messagetype="assistant",
    message="👋 Hi, booklover!"
)
with app.app_context():
    db.session.add(initial_message)
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def home():
    # Retrieve all entries from the Communications table
    result = db.session.execute(db.select(Communications))
    all_communications = result.scalars()

    # Create an instance of the chat form
    form = ChatForm()
    if form.validate_on_submit():
        # Get user question from the form
        user_question = form.question.data
        # Add user question to the database
        new_user_entry = Communications(
            time=datetime.now().strftime('%H:%M'),
            messagetype="user",
            message=user_question
        )
        db.session.add(new_user_entry)

        # Get bot reply and add to the database
        bot_reply = get_system_reply(user_question)
        new_bot_entry = Communications(
            time=datetime.now().strftime('%H:%M'),
            messagetype="assistant",
            message=bot_reply
        )
        db.session.add(new_bot_entry)
        db.session.commit()

        # Redirect to home to display the new conversation
        return redirect(url_for('home'))

    # Render the home template with the chat form and previous conversations
    return render_template("index.html", form=form, conversations=all_communications)


# Run the app
if __name__ == "__main__":
    app.run(debug=False, port=5000)
