from flask import render_template, abort, redirect, request, url_for
import mistune

from . import app
from .database import session, Entry

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
def add_entry_get():
    return render_template("add_entry.html")
    
from flask import request, redirect, url_for

@app.route("/entry/add", methods=["POST"])
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
    
@app.route("/entry/<int:entry_id>")
def single_entry(entry_id):
	entry = session.query(Entry).filter(Entry.id==entry_id).first()
	return render_template("single_entry.html",entry=entry)
	
@app.route("/entry/<int:entry_id>/edit", methods=["GET"])
def edit_entry_get(entry_id):
    entry = session.query(Entry).get(entry_id)
    return render_template("edit_entry.html", entry=entry)

@app.route("/entry/<int:entry_id>/edit", methods=["POST"])
def edit_entry_entry(entry_id):
    if  request.method == "POST":
        entry = session.query(Entry).get(entry_id)
        entry.title=request.form["title"],
        entry.content=mistune.markdown(request.form["content"])
        session.add(entry)
        session.commit()
        return redirect(url_for("entries"))
        
    entry = session.query(Entry).get(entry_id)
    return render_template("edit_entry.html", entry=entry)
    
@app.route("/entry/<int:entry_id>/delete", methods=["GET","POST"])
def delete_entry_get(entry_id=1):
    entry = session.query(Entry).get(entry_id)
    if entry is None:
        abort(404)
    return render_template("delete_entry.html", entry=entry)

@app.route("/delete/confirmation/<int:entry_id>", methods=["GET"])
def delete_entry_confirmed(entry_id):
    entry = session.query(Entry).get(entry_id)
    if entry is None:
        abort(404)
    session.delete(entry)
    session.commit()
    return render_template("delete_confirmation.html")
    