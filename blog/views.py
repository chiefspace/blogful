from flask import render_template
import mistune

from . import app
from .database import session, Entry

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1, methods=["GET"]):
    
    try:
        paginate_by = int(request.args.get('limit'))

    except TypeError:
        paginate_by = 5
        
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()
    
    if paginate_by > count:
        paginate_by = count

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) // paginate_by + 1
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
        total_pages=total_pages
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
def view_entry(entry_id):
	entry = session.query(Entry).filter(Entry.id==entry_id).first()
	return render_template("single_entry.html",entry=entry)
	
@app.route("/entry/<int:entry_id>/edit", methods=["GET"])
def edit_entry_get(entry_id):
    entry = session.query(Entry).get(entry_id)
    return render_template("edit_entry.html", entry=entry)

@app.route("/entry/<int:entry_id>/edit", methods=["POST"])
def edit_entry_entry(entry_id):
    entry = session.query(Entry).get(entry_id)
    entry.title=request.form["title"],
    entry.content=mistune.markdown(request.form["content"])
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))
  
@app.route("/entry/<int:entry_id>/delete", methods=["GET","POST"])
def delete_entry(entry_id):
    entry = session.query(Entry).filter(Entry.id==entry_id).first()
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))
    