import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

############################
# Application configurations
############################
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hard to guess string from si364'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/krguHW5"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


#########################
##### Set up Models #####
#########################

## All provided.

# Association table
on_list = db.Table('on_list',db.Column('item_id',db.Integer, db.ForeignKey('items.id')),db.Column('list_id',db.Integer, db.ForeignKey('lists.id')))

class TodoList(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(225))
    items = db.relationship('TodoItem',secondary=on_list,backref=db.backref('lists',lazy='dynamic'),lazy='dynamic')

class TodoItem(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(225))
    priority = db.Column(db.Integer)


########################
##### Set up Forms #####
########################

# Provided - Form to create a todo list
class TodoListForm(FlaskForm):
    name = StringField("What is the title of this TODO List?", validators=[Required()])
    items = TextAreaField("Enter your TODO list items in the following format: Description, Priority -- separated by newlines")
    submit = SubmitField("Submit")


class UpdateButtonForm(FlaskForm):
    submit = SubmitField('Update')


class UpdateInfoForm(FlaskForm):
    new_priority = StringField("What is the new priority of this item?", validators=[Required()])
    submit = SubmitField('Update')


class DeleteButtonForm(FlaskForm):
    submit = SubmitField('Delete')


################################
####### Helper Functions #######
################################

## Provided.

def get_or_create_item(item_string):
    elements = [x.strip().rstrip() for x in item_string.split(",")]
    item = TodoItem.query.filter_by(description=elements[0]).first()
    if item:
        return item
    else:
        item = TodoItem(description=elements[0],priority=elements[-1])
        db.session.add(item)
        db.session.commit()
        return item

def get_or_create_todolist(title, item_strings=[]):
    l = TodoList.query.filter_by(title=title).first()
    if not l:
        l = TodoList(title=title)
    for s in item_strings:
        item = get_or_create_item(s)
        l.items.append(item)
    db.session.add(l)
    db.session.commit()
    return l


###################################
##### Routes & view functions #####
###################################

# Provided
@app.route('/', methods=["GET","POST"])
def index():
    form = TodoListForm()
    if request.method=="POST":
        title = form.name.data
        items_data = form.items.data
        new_list = get_or_create_todolist(title, items_data.split("\n"))
        return redirect(url_for('all_lists'))
    return render_template('index.html',form=form)

# Provided - see below for additional TODO
@app.route('/all_lists',methods=["GET","POST"])
def all_lists():
    form = DeleteButtonForm()
    lsts = TodoList.query.all()
    return render_template('all_lists.html',todo_lists=lsts, form=form)


# Provided - see below for additional TODO
@app.route('/list/<ident>',methods=["GET","POST"])
def one_list(ident):
    form = UpdateButtonForm()
    lst = TodoList.query.filter_by(id=ident).first()
    items = lst.items.all()
    return render_template('list_tpl.html',todolist=lst,items=items,form=form)



@app.route('/update/<item>',methods=["GET","POST"])
def update(item):
    form = UpdateInfoForm()
    if form.validate_on_submit():
        new_priority = form.new_priority.data
        i = TodoItem.query.filter_by(description=item).first()
        i.priority = new_priority
        db.session.commit()
        flash("Updated priority of " + item)
        return redirect(url_for('all_lists'))
    return render_template('update_item.html',item = item, form = form)



@app.route('/delete/<lst>',methods=["GET","POST"])
def delete(lst):
    l = TodoList.query.filter_by(title=lst).first()
    db.session.delete(l)
    db.session.commit()
    flash("Deleted list {}".format(lst))
    return redirect(url_for('all_lists'))


if __name__ == "__main__":
    db.create_all()
    manager.run()
