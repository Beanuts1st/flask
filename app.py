import io
from flask import Flask, request, render_template, redirect, url_for,flash
from flask_login import UserMixin, LoginManager, login_user,logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image, ImageOps
from passlib.hash import scrypt

app = Flask(__name__)
app.secret_key = 'AcSIWq5E0Rej'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neonsql_owner:AcSIWq5E0Rej@ep-royal-king-a1z6svb5.ap-southeast-1.aws.neon.tech/neonsql?sslmode=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
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

class SuperUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    # Flask-Login integration
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return SuperUser.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = SuperUser.query.filter_by(username=username).first()
        if user:
            print("User found:", user.username)
            if scrypt.verify(password, user.password):
                print("Password matches")
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                print("Password does not match")
        else:
            print("User not found")
        flash('Invalid username or password', 'danger')
    return render_template('/cms/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Jumlah properti per halaman
    properties = Property.query.order_by(Property.date_added.desc()).paginate(page=page, per_page=per_page)
    return render_template('/cms/dashboard.html', properties=properties)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
def home():
    properties = Property.query.all()
    hero_template='components/home_hero.html'
    return render_template('/pages/home.html', properties=properties, hero_template=hero_template)

@app.route('/contact')
def contact():
    hero_template='components/default_hero.html'
    title='Contact Us'
    return render_template('/pages/contact.html', title=title, hero_template=hero_template)

@app.route('/about')
def about():
    hero_template='components/default_hero.html'
    title='About'
    return render_template('/pages/about.html', title=title, hero_template=hero_template)

@app.route('/services')
def services():
    categories = [
        "Architectural design and planning",
        "Land investigation",
        "Notary service",
        "Due diligence",
        "Establish building permit",
        "Establish building construction",
        "Land topography measurement",
        "Determination map boundary",
        "Villa management",
        "Establish foreign investment company in Indonesia ( PT. PMA )",
        "Establish Business permit",
        "Land Acquisition",
        "Theodolit format Autocad"
    ]
    hero_template='components/default_hero.html'
    title='About'
    return render_template('/pages/services.html', categories=categories,title=title, hero_template=hero_template)

@app.route('/properties', methods=['GET'])
def view_property():
    page = request.args.get('page', 1, type=int)
    property_type = request.args.get('type')
    sort_by = request.args.get('sort')

    query = Property.query

    if property_type:
        query = query.filter_by(type=property_type)

    if sort_by == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Property.date_added.asc())
    elif sort_by == 'date_desc':
        query = query.order_by(Property.date_added.desc())
    else:
        query = query.order_by(Property.date_added.desc())

    properties = query.paginate(page=page, per_page=5)
    prev_url = url_for('view_property', page=properties.prev_num) if properties.has_prev else None
    next_url = url_for('view_property', page=properties.next_num) if properties.has_next else None
    hero_template='components/default_hero.html'
    title='Properties'
    return render_template('/pages/properties.html',title=title, properties=properties.items, pagination=properties, prev_url=prev_url, next_url=next_url,hero_template=hero_template)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    hero_template='components/default_hero.html'
    title='Detail Property'
    return render_template('/pages/detail_property.html',title=title, property=property,hero_template=hero_template)

@app.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        type = request.form['type']
        date_added = datetime.utcnow()

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
                
                # Resize the image to 1080x1080 using PIL
                image = Image.open(file)
                image = ImageOps.fit(image, (1080, 1080), Image.Resampling.LANCZOS)
                
                # Save the image to a BytesIO object
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Encode the image to base64
                encoded_string = base64.b64encode(img_byte_arr).decode('utf-8')

                new_image = PropertyImage(property_id=new_property.id, image_data=encoded_string)
                db.session.add(new_image)
                db.session.commit()
        
        return redirect(url_for('dashboard'))
    return render_template('/cms/add_property.html')

@app.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)

    if request.method == 'POST':
        # Perbarui properti
        property.title = request.form['title']
        property.description = request.form['description']
        property.price = request.form['price']
        property.location = request.form['location']
        property.type = request.form['type']
        property.date_added = datetime.strptime(request.form['date_added'], '%Y-%m-%dT%H:%M')

        # Hapus gambar lama
        PropertyImage.query.filter_by(property_id=property.id).delete()

        # Simpan perubahan properti
        db.session.commit()

        # Tambahkan gambar-gambar baru
        files = request.files.getlist('images')
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                
                # Resize the image to 1080x1080 using PIL
                image = Image.open(file)
                image = ImageOps.fit(image, (1080, 1080), Image.Resampling.LANCZOS)
                
                # Save the image to a BytesIO object
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Encode the image to base64
                encoded_string = base64.b64encode(img_byte_arr).decode('utf-8')

                new_image = PropertyImage(property_id=property.id, image_data=encoded_string)
                db.session.add(new_image)
                db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('/cms/edit.html', property=property)

@app.route('/delete_property/<int:property_id>', methods=['POST'])
def delete_property(property_id):
    property_to_delete = Property.query.get(property_id)
    if property_to_delete:
        # Hapus gambar terkait dengan properti yang akan dihapus
        PropertyImage.query.filter_by(property_id=property_id).delete()
        
        db.session.delete(property_to_delete)
        db.session.commit()
        flash('Property and associated images deleted successfully', 'success')
    else:
        flash('Property not found', 'danger')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
