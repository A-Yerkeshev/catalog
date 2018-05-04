import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, login_required, login_user
from flask_login import logout_user, current_user
from flask_uploads import UploadSet, IMAGES, configure_uploads
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, User
from passlib.apps import custom_app_context

app = Flask(__name__)
app.secret_key = 'catalog'
app.config['UPLOADED_IMAGES_DEST'] = 'static/img/uploads'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()

login_manager = LoginManager()
login_manager.init_app(app)


# Define all necessary functions for users registration and authorization
@login_manager.user_loader
def load_user(id):
    return session.query(User).filter_by(id=id).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


def hash_password(password):
    return custom_app_context.encrypt(password)


# Register new user
@app.route('/register/', methods=['GET', 'POST'])
def register():
    rep_form = '''<label for="password">Repeat password:</label>
            <input type="password" name="repeat" class="input" required
            maxlength=50>'''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repeat = request.form.get('repeat')
        if password != repeat:
            return render_template('users.html').format(
                get_categories(), 'Register new user', '''! Passwords does not
                match''', rep_form, 'Register')
        if session.query(User).filter_by(
            username=username).first() is not None:
            return render_template('users.html').format(
                get_categories(), 'Register new user', '! User already exist',
                rep_form, 'Register')
        user = User(
            username=username, pass_hash=hash_password(password),
            status='user')
        session.add(user)
        session.commit()
        login_user(user)
        return redirect(url_for('main'))
    else:
        return render_template('users.html').format(
            get_categories(), 'Register new user', '', rep_form, 'Register')


# Verify the password
def verify_password(password, pass_hash):
    return custom_app_context.verify(password, pass_hash)


# Login the user
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = session.query(User).filter_by(username=username).first()
        if user != None:
            if verify_password(password, user.pass_hash):
                login_user(user)
                return redirect(url_for('main'))
            else:
                return render_template('users.html').format(
                    get_categories(), 'Log in', '''! Username or password is
                    incorrect''', '', 'Log in')
        else:
            return render_template('users.html').format(
                get_categories(), 'Log in', '''! User does not exist''', '', 'Log in')			
    else:
        return render_template('users.html').format(
            get_categories(), 'Log in', '', '', 'Log in')


def logged_user():
    if current_user.is_active is True:
        return current_user.username
    else:
        return None


# Logout the user
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


# Define function that retrieves categories list from the database
def get_categories():
    query = session.query(
        Item.category, func.min(Item.id)).group_by(Item.category).all()
    categories = ''
    for c in query:
        categories += (
            '<li><a href="/'+str(c[0])+'" class="category">' + str(c[0]) +
            '</a></li>')
    return categories


# Home page
@app.route('/')
def main():
    query = session.query(
        Item.name, Item.category, Item.id).order_by(
            Item.id.desc()).limit(50).all()
    items = ''
    for r in query:
        items += (
            '<li><a href="/'+str(r[1])+'/'+str(r[2])+'" class="item">' +
            str(r[0]) + '</a><span class="extra"> ('+str(r[1])+')</span></li>')
    count = session.query(Item).count()
    return render_template('index.html').format(
        get_categories(), count, items, logged_user())


# Display all items for selected category
@app.route('/<string:category>/')
def get_items(category):
    query = session.query(Item.name, Item.id).filter_by(
        category=category).all()
    items = ''
    for i in query:
        items += (
            '<li><a href="/' + category+'/' + str(i[1]) + '" class="item">' +
            str(i[0])+'</a></li>')
    count = session.query(Item).filter_by(category=category).count()
    return render_template('category.html').format(
        get_categories(), category, count, items, logged_user())


# Show description for selected item
@app.route('/<string:category>/<int:id>')
def get_description(category, id):
    query = session.query(
        Item.description, Item.name, Item.image, Item.user_id).filter_by(
            id=id).first()
    if query[2] is not None:
        image = '<img src="/static/img/uploads/'
        + str(query[2]) + '" alt="item-image" class="item-image">'
    else:
        image = ''
    return render_template(
        'description.html', category=category, id=id,
        user_id=int(query[3])).format(
            get_categories(), str(query[1]), image, str(query[0]),
            logged_user())


# Add new item
@app.route('/add', methods=['GET', 'POST'])
@app.route('/<string:category>/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == "POST":
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        image = request.files.get('image')
        if image is not None:
            filename = images.save(image)
        else:
            filename = None
        item = Item(
            name=name, category=category, description=description,
            image=filename, user_id=current_user.id)
        session.add(item)
        session.commit()
        return redirect(url_for('main'))
    else:
        return render_template('item.html').format(
            get_categories(), 'Add new', logged_user())


# Edit the item
@app.route('/<string:category>/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(category, id):
    query = session.query(Item).filter_by(id=id).one()
    if request.method == 'POST':
        query.name = request.form.get('name')
        query.category = request.form.get('category')
        query.description = request.form.get('description')
        session.commit()
        return redirect(url_for(
            'get_description', category=query.category, id=query.id))
    else:
        name = query.name
        category = query.category
        description = query.description
        return render_template(
            'item.html', name=name, category=category,
            description=description).format(
                get_categories(), 'Edit this', logged_user())


# Delete the item
@app.route('/<string:category>/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_item(category, id):
    query = session.query(Item).filter_by(id=id).one()
    if request.method == 'POST':
        session.delete(query)
        session.commit()
        return redirect(url_for('get_items', category=category))
    else:
        return render_template(
            'delete.html', category=category, id=id, name=Item.name).format(
                get_categories(), logged_user())


# Send JSON
@app.route('/json')
def send_json():
    query = session.query(Item.category, func.min(Item.id)).group_by(
        Item.category).all()
    categories = []
    for i in query:
        categories.append(i[0])
    items = []
    for cat in categories:
        query = session.query(Item).filter_by(category=cat).all()
        for item in query:
            items.append({
                    "item_id": item.id,
                    "name": item.name,
                    "category": item.category,
                    "description": item.description,
                    "image_url": item.image,
                    "author_id": item.user_id
                })
    response = {}
    for i in range(0, len(categories)):
        for item in items:
            if item['category'] == categories[i]:
                if categories[i] in response:
                    response[categories[i]].append(item)
                else:
                    response[categories[i]] = [item]
    response = {
            'Categories': response
        }
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)

session.close()
