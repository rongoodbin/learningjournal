from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask_login import LoginManager, login_user, logout_user, \
                        login_required, current_user
import models
import forms
from flask_bcrypt import check_password_hash


DEBUG = True
PORT = 8000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = "spfr=iogr-=ikagpkjope2="

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response



@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you registered!", "success")
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


#/’ /entries /entries/<slug> /entries/edit/<slug> /entries/delete/<slug> /entry

@app.route('/entries/<int:entry_id>', methods=('GET', 'POST'))
@app.route('/entries')
def entries(entry_id=None):
    if not entry_id:
           entries = models.Journal.select().limit(100)
           return render_template('index.html', entries=entries)
    else:
        entry = models.Journal.get(models.Journal.id == entry_id)
        print(entry.title)
        return render_template('detail.html', entry=entry)


@app.route('/entries/edit/<int:entry_id>', methods=('GET', 'POST'))
def edit(entry_id):
    if not entry_id:
          return redirect(url_for('entries'))

    form = forms.EntryForm()
    entry = models.Journal.get(models.Journal.id == entry_id)

    if form.validate_on_submit():
        entry.title = form.title.data
        entry.entrydate = form.date.data
        entry.timespent = form.timespent.data
        entry.learned = form.learned.data
        entry.resources = form.resources.raw_data
        entry.save
        return render_template('detail.html', entry=entry)
    else:
        form.title.data = entry.title
        form.date.data = entry.entrydate
        form.timespent.data = entry.timespent
        form.learned.data = entry.learned
        form.resources.data = entry.resources
        return render_template('edit.html', form=form, entry=entry)


@app.route('/')
def index():
    return redirect(url_for('entries'))


@app.route('/newentry',  methods=('GET', 'POST') )
@login_required
def newentry():
    form = forms.EntryForm()
    if form.validate_on_submit():
            models.Journal.create_entry(
                title=form.title.data,
                entrydate=form.date.data,
                user=g.user.id,
                timespent=form.timespent.data,
                learned=form.learned.data,
                resources=form.resources.raw_data
            )
            return redirect(url_for('index'))
    return render_template('new.html',form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)