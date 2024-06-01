from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]= "postgresql://neonsql_owner:AcSIWq5E0Rej@ep-royal-king-a1z6svb5.ap-southeast-1.aws.neon.tech/neonsql?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Create a simple model
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='select')
    images = db.relationship('PropertyImage', backref='property', lazy=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

# Model PropertyImage (sesuaikan dengan kebutuhan Anda)
class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)

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

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        type = request.form['type']
        date_added = request.form['date_added']
        
        new_property = Property(
            title=title,
            description=description,
            price=price,
            location=location,
            type=type,
            date_added=date_added
        )
        
        db.session.add(new_property)
        db.session.commit()
        
        return redirect(url_for('home'))
    return render_template('add_property.html')

if __name__ == '__main__':
    app.run(debug=True)