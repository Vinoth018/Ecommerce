import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:0108@localhost:5432/Ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/product_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    image = db.Column(db.String(120), nullable=True)


# Create tables
with app.app_context():
    db.create_all()

# Categories
categories = ["Tshirt", "Shirt", "Pant", "Tracks", "Shorts"]

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home page - category listing
@app.route('/')
def index():
    return render_template('index.html', categories=categories)

# Category page - list products
@app.route('/category/<category>', methods=['GET'])
def show_category(category):
    search = request.args.get('search', '').lower()
    products = Product.query.filter(Product.category == category)

    if search:
        products = products.filter(Product.name.ilike(f'%{search}%'))

    products = products.all()
    return render_template('category.html', category=category, products=products)

# Product detail
@app.route('/product/<int:pid>')
def product_detail(pid):
    product = Product.query.get_or_404(pid)
    return render_template('product_detail.html', product=product)

# Admin panel - Add product
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        description = request.form.get('description', '')
        
        # Handling image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename

        # Ensure category is valid
        if category not in categories:
            return "Invalid category!", 400

        new_product = Product(name=name, category=category, price=price, stock=stock, description=description, image=image)
        db.session.add(new_product)
        db.session.commit()

    products = Product.query.all()
    return render_template('admin.html', products=products)

# Delete product (admin)
@app.route('/admin/delete/<int:pid>')
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    if product.image:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin'))

# Add product to cart
@app.route('/cart/add/<int:pid>')
def add_to_cart(pid):
    cart = session.get('cart', [])
    if pid not in cart:
        cart.append(pid)
    session['cart'] = cart
    return redirect(url_for('cart'))

# View cart
@app.route('/cart')
def cart():
    cart_ids = session.get('cart', [])
    cart_items = Product.query.filter(Product.id.in_(cart_ids)).all()
    return render_template('cart.html', products=cart_items)

# Remove product from cart
@app.route('/cart/remove/<int:pid>')
def remove_from_cart(pid):
    cart = session.get('cart', [])
    if pid in cart:
        cart.remove(pid)
    session['cart'] = cart
    return redirect(url_for('cart'))

# Place order
@app.route('/order')
def place_order():
    cart = session.get('cart', [])
    for pid in cart:
        orders.append({'product_id': pid})
    session['cart'] = []
    return "<h3>✅ Order placed successfully! <a href='/'>Go back</a></h3>"

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5001)
