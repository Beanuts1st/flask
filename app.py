from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import base64
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neonsql_owner:AcSIWq5E0Rej@ep-royal-king-a1z6svb5.ap-southeast-1.aws.neon.tech/neonsql?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False, default='select')
    images = db.relationship('PropertyImage', backref='property', lazy=True)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_data = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    properties = Property.query.all()
    return render_template('home.html', properties=properties)

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        type = request.form['type']
        date_added = datetime.strptime(request.form['date_added'], '%Y-%m-%dT%H:%M')

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

        # Handling image uploads
        files = request.files.getlist('images')
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file_data = file.read()
                encoded_string = base64.b64encode(file_data).decode('utf-8')

                new_image = PropertyImage(property_id=new_property.id, image_data=encoded_string)
                db.session.add(new_image)
                db.session.commit()
        
        return redirect(url_for('home'))
    return render_template('add_property.html')

if __name__ == '__main__':
    app.run(debug=True)
