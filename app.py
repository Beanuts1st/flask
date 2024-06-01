from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]= "postgresql://neonsql_owner:AcSIWq5E0Rej@ep-royal-king-a1z6svb5.ap-southeast-1.aws.neon.tech/neonsql?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Create a simple model
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

# Commit your model (table) to the database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Home Page!"

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        new_book = Book(title=title)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_book.html')


if __name__ == '__main__':
    app.run(debug=True)