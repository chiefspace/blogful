from flask import render_template, abort, redirect, request, url_for
import mistune

from . import app
from .database import session, Entry

from flask.ext.login import login_required
from werkzeug.exceptions import Forbidden

@app.route("/", methods=["GET","POST"])
@app.route("/page/<int:page>", methods=["GET","POST"])
@app.route("/?limit=<int:per_page>", methods=["GET","POST"])
@app.route("/page/<int:page>?limit=<int:per_page>", methods=["GET","POST"])
def entries(page=1):
        
    # Zero-indexed page
    page_index = page - 1

    if request.args.get('limit'):
        per_page = request.args.get('limit', type=int)  # if limit is added to the url
    else:
        per_page = 10  # default

    count = session.query(Entry).count()
    
    if per_page > count:
        per_page = count

    start = page_index * per_page
    end = start + per_page

    total_pages = (count - 1) // per_page + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        per_page=per_page
    )
    
@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")
    
from flask import request, redirect, url_for

from flask.ext.login import current_user

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<int:entry_id>")
def single_entry(entry_id):
	entry = session.query(Entry).filter(Entry.id==entry_id).first()
	return render_template("single_entry.html",entry=entry)
	
@app.route("/entry/<int:entry_id>/edit", methods=["GET"])
@login_required
def edit_entry_get(entry_id):
    entry = session.query(Entry).get(entry_id)
    
    if not all([entry.author, current_user]) or entry.author.id != current_user.id:
        raise Forbidden('Only entry author can edit their own entry.')
    
    return render_template("edit_entry.html", entry=entry)

@app.route("/entry/<int:entry_id>/edit", methods=["POST"])
@login_required
def edit_entry_entry(entry_id):
    if  request.method == "POST":
        entry = session.query(Entry).get(entry_id)
        entry.title=request.form["title"],
        entry.content=mistune.markdown(request.form["content"])
        session.add(entry)
        session.commit()
        return redirect(url_for("entries"))
        
#    entry = session.query(Entry).get(entry_id)
#    return render_template("edit_entry.html", entry=entry)
    
@app.route("/entry/<int:entry_id>/delete", methods=["GET","POST"])
@login_required
def delete_entry_get(entry_id=1):
    entry = session.query(Entry).get(entry_id)
    
    if not all([entry.author, current_user]) or entry.author.id != current_user.id:
        raise Forbidden('Only entry author can d their own entry.')
    
    if entry is None:
        abort(404)
    return render_template("delete_entry.html", entry=entry)

@app.route("/delete/confirmation/<int:entry_id>", methods=["GET"])
@login_required
def delete_entry_confirmed(entry_id):
    entry = session.query(Entry).get(entry_id)
    if entry is None:
        abort(404)
    session.delete(entry)
    session.commit()
    return render_template("delete_confirmation.html")
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")
    
from flask import flash
from flask.ext.login import login_user, logout_user
from werkzeug.security import check_password_hash
from .database import User

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
        
        
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect(url_for("login_get"))
    