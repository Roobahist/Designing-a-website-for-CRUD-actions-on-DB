from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base, generate_relationship
from sqlalchemy import inspect


app = Flask(__name__)
app.secret_key = 'super secret key'
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/db_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Base = automap_base()

Base.prepare(db.engine, reflect=True)

course = Base.classes.course #skill_collection, employee_collection
skill = Base.classes.skill #employee_collection, course_collection
employee = Base.classes.employee #skill_collection, course_collection
course_class_days = Base.classes.course_class_days
department = Base.classes.department
employee_takes_exam = Base.classes.employee_takes_exam
role = Base.classes.role
teacher = Base.classes.teacher


def join(l, sep):
    out_str = ''
    for i, el in enumerate(l):
        out_str += '{}{}'.format(el, sep)
    return out_str[:-len(sep)]


def other_tables(to_exclude):
    all_tables = ['course','course_gives_skill','department','employee','employee_attends_course','employee_has_skill','employee_takes_exam','role','skill','teacher']
    all_tables.remove(to_exclude)
    return all_tables
 
 
@app.route('/delete/<table>/<filters>')
def delete(table,filters):
    all_records = db.session.query(eval(table))

    filters = filters.split('-')
    for f in filters:
        col, val = f.split('=')
        all_records = all_records.filter(getattr(eval(table),col)==val)
    
    record = all_records.first()

    db.session.delete(record)
    db.session.commit()

    # flash("Employee Deleted Successfully")
    return redirect('/'+table)


@app.route('/insert/<table>', methods = ['POST'])
def insert(table):
    if request.method == 'POST':
        days = []
        data = dict()
        for key, value in request.form.items():
            if 'weekday' in key:
                days.append(key[8:])
                continue
            else:
                data[key] = value

        record = eval(table)(**data)
        db.session.add(record)
        db.session.commit()

        if table == 'course':
            for day in days:
                record = course_class_days(course_id=data['course_id'],holding_day=day)
                db.session.add(record)
                db.session.commit()

        return redirect('/'+table)


@app.route('/update/<table>/<filters>', methods = ['POST'])
def update(table,filters):
    all_records = db.session.query(eval(table))

    filters = filters.split('-')
    for f in filters:
        col, val = f.split('=')
        all_records = all_records.filter(getattr(eval(table),col)==val)
    
    days = []
    data = dict()
    for key, value in request.form.items():
        if 'weekday' in key:
            days.append(key[8:])
            continue
        else:
            data[key] = value

    all_records.update(data, synchronize_session='evaluate')

    if table == 'course':
        all_course_class_days = db.session.query(course_class_days)
        all_course_class_days.filter(getattr(course_class_days,'course_id')==data['course_id']).delete(synchronize_session=False)

        for day in days:
            record = course_class_days(course_id  = request.form['course_id'],
                                        holding_day = day)
            db.session.add(record)

    db.session.commit()

    return redirect('/'+table)


@app.route('/delete/relation/<relation_table_name>/<filters>')
def delete_relation(relation_table_name,filters):
    parsed = relation_table_name.split('_')
    table_1 = parsed[0]
    table_2 = parsed[2]

    filters_parsed = []
    filters = filters.split('-')
    for f in filters:
        col, val = f.split('=')
        filters_parsed.append([col, val])

    table_1_recrod = db.session.query(eval(table_1)).filter(getattr(eval(table_1),filters_parsed[0][0])==filters_parsed[0][1]).first()
    table_2_recrod = db.session.query(eval(table_2)).filter(getattr(eval(table_2),filters_parsed[1][0])==filters_parsed[1][1]).first()

    getattr(table_1_recrod,table_2+'_collection').remove(table_2_recrod)
    db.session.commit()

    return redirect('/relation/'+relation_table_name)


@app.route('/insert/relation/<relation_table_name>', methods=['POST'])
def insert_relation(relation_table_name):
    parsed = relation_table_name.split('_')
    table_1 = parsed[0]
    table_2 = parsed[2]

    col1, col2 = list(request.form.keys())
    val1, val2 = list(request.form.values())

    table_1_recrod = db.session.query(eval(table_1)).filter(getattr(eval(table_1),col1)==val1).first()
    table_2_recrod = db.session.query(eval(table_2)).filter(getattr(eval(table_2),col2)==val2).first()

    getattr(table_1_recrod,table_2+'_collection').append(table_2_recrod)
    db.session.commit()

    return redirect('/relation/'+relation_table_name)


@app.route('/update/relation/<relation_table_name>/<filters>', methods=['POST'])
def update_relation(relation_table_name,filters):
    parsed = relation_table_name.split('_')
    table_1 = parsed[0]
    table_2 = parsed[2]

    #delete
    filters_parsed = []
    filters = filters.split('-')
    for f in filters:
        col, val = f.split('=')
        filters_parsed.append([col, val])

    table_1_recrod = db.session.query(eval(table_1)).filter(getattr(eval(table_1),filters_parsed[0][0])==filters_parsed[0][1]).first()
    table_2_recrod = db.session.query(eval(table_2)).filter(getattr(eval(table_2),filters_parsed[1][0])==filters_parsed[1][1]).first()

    getattr(table_1_recrod,table_2+'_collection').remove(table_2_recrod)
    db.session.commit()

    #insert
    col1, col2 = list(request.form.keys())
    val1, val2 = list(request.form.values())

    table_1_recrod = db.session.query(eval(table_1)).filter(getattr(eval(table_1),col1)==val1).first()
    table_2_recrod = db.session.query(eval(table_2)).filter(getattr(eval(table_2),col2)==val2).first()

    getattr(table_1_recrod,table_2+'_collection').append(table_2_recrod)
    db.session.commit()


    return redirect('/relation/'+relation_table_name)


@app.route('/course')
def course_webpage():
    courses = db.session.query(course).all()
    print(len(courses))
    days = []
    for c in courses:
        id = c.course_id
        d = db.session.query(course_class_days).filter_by(course_id=id)
        days.append(join([day.holding_day for day in d] ,' - '))

    return render_template('course.html', to_pass=zip(courses,days), other_tables=other_tables('course'))


@app.route('/<table>')
def basic_webpage(table):
    table_records = db.session.query(eval(table)).all()
    webpage_name = table+'.html'
    return render_template(webpage_name, table_records=table_records, other_tables=other_tables(table))


@app.route('/relation/<relation_table_name>')
def relation_webpage(relation_table_name):
    parsed = relation_table_name.split('_')
    table_1 = parsed[0]
    table_2 = parsed[2]

    table_1_id = []
    table_2_id = []

    table1_all_records = db.session.query(eval(table_1)).all()
    for record in table1_all_records:
        related_records = getattr(record,table_2+'_collection')
        for related in related_records:
            table_1_id.append(getattr(record,table_1+'_id'))
            table_2_id.append(getattr(related,table_2+'_id'))

    column_names = [table_1+'_id',table_1+'_id']

    webpage_name = relation_table_name+'.html'
    return render_template(webpage_name, table_records=zip(table_1_id,table_2_id), other_tables=other_tables(relation_table_name))


app.run(host='localhost', port=5000, debug=True)