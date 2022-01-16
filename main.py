import io
from flask import Flask, render_template, request, redirect, url_for, send_file, g, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.utils import secure_filename
import  os
from base64 import b64encode, b64decode
import  base64
from io import  BytesIO
from PIL import Image
import win32api


app = Flask(__name__)

app.secret_key = os.urandom(24)

#Database configuration

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'project'

mysql = MySQL(app)
@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('adno',None)
        userdetails = request.form
        ad = userdetails['adno']
        ps = userdetails['password']
        cur = mysql.connection.cursor()
        sql = "select * from trial where adno=%s and psw=%s"
        adr = (ad, ps)
        result = cur.execute(sql, adr)
        if result > 0:
            userdetails1 = cur.fetchall()
            session['adno'] = userdetails1[0][3]
            return redirect(url_for('users'))
        else:
            win32api.MessageBox(0, 'Invalid username or password', 'error', 0x00001000)
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def test():
    if request.method == 'POST':
        #Fetch form html
        userdetails = request.form
        fn = userdetails['fname']
        ln = userdetails['lname']
        ad = userdetails['adno']
        pn = userdetails['pno']
        eps = userdetails['epsw']
        cps = userdetails['cpsw']
        cy = userdetails['city']
        pc = userdetails['pcode']
        an = userdetails['dob']
        prof =userdetails['profession']
        ty = userdetails['type']
        gen = userdetails['gender']
        ch = userdetails.getlist('ch[]')
        lang=""
        for i in range(0,len(ch)):
            if i==0:
                lang=lang+ch[i]
            else:
                lang=lang+", "+ch[i]
        file=request.files['image']
        data = file.read()
        #Cursor
        cur = mysql.connection.cursor()
        if eps == cps:
            cur.execute("INSERT INTO trial(fname, lname, adno, pno, psw, city, pcode, dob, profession, lang, gender, pic, type) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fn, ln, ad, pn, eps, cy, pc, an, prof, lang, gen, data, ty))
            mysql.connection.commit()
            cur.close()
            win32api.MessageBox(0,'Account Created Successfully','Congratulations',0x00001000)
            return redirect(url_for('login'))
        else:
            win32api.MessageBox(0, 'Check your password', 'error',0x00001000)
    return render_template('signup.html')

@app.route('/users')
def users():
    if g.adno:
        cur = mysql.connection.cursor()
        sql = "select * from trial where adno = %s"
        adr = (g.adno, )
        result = cur.execute(sql, adr)
        if result > 0:
            userdetails1 = cur.fetchall()
            fn = userdetails1[0][1]
            ln = userdetails1[0][2]
            ad = userdetails1[0][3]
            pn = userdetails1[0][4]
            cy = userdetails1[0][6]
            pc = userdetails1[0][7]
            an = userdetails1[0][8]
            prof = userdetails1[0][9]
            ty = userdetails1[0][13]
            gen = userdetails1[0][11]
            lang = userdetails1[0][10]
            userdetails = userdetails1[0][12]
            img = b64encode(userdetails).decode("utf-8")
            return render_template('home.html', userdetails = img, fname = fn, lname = ln, adno = ad, pno = pn, city = cy, pcode = pc, dob = an , profession = prof, type = ty, gender = gen, language = lang )
    else:
        win32api.MessageBox(0, 'Logout Successfully', 'Congratulations', 0x00001000)
        return redirect(url_for('login'))

@app.route('/search')
def search():
    if g.adno:
        cur = mysql.connection.cursor()
        result = cur.execute('select fname, lname, type, profession, city, adno, pic, id from trial')
        if result > 0:
            userdetails1 = cur.fetchall()
            us1 = list(userdetails1)
            for i in range(0,len(us1)):
                us2 = list(us1[i])
                userdetails = us2[6]
                img = b64encode(userdetails).decode("utf-8")
                us2[6] = img
                us1[i] = tuple(us2)
            userdetails1 = tuple(us1)
            return render_template('search.html', data = userdetails1 )
    else:
        win32api.MessageBox(0, 'Logout Successfully', 'Congratulations', 0x00001000)
        return redirect(url_for('login'))

@app.route('/user', methods = ['GET', 'POST'])
def selectedUser():
    if request.method == 'POST':
        uid = request.form.get("msgid")
        cur = mysql.connection.cursor()
        sql = "select * from trial where id = %s"
        adr = (uid, )
        result = cur.execute(sql, adr)
        if result > 0:
            userdetails1 = cur.fetchall()
            fn = userdetails1[0][1]
            ln = userdetails1[0][2]
            ad = userdetails1[0][3]
            pn = userdetails1[0][4]
            cy = userdetails1[0][6]
            pc = userdetails1[0][7]
            an = userdetails1[0][8]
            prof = userdetails1[0][9]
            ty = userdetails1[0][13]
            gen = userdetails1[0][11]
            lang = userdetails1[0][10]
            userdetails = userdetails1[0][12]
            img = b64encode(userdetails).decode("utf-8")
            return render_template('home.html', userdetails = img, fname = fn, lname = ln, adno = ad, pno = pn, city = cy, pcode = pc, dob = an , profession = prof, type = ty, gender = gen, language = lang )

@app.before_request
def before_request():
    g.adno = None
    if 'adno' in session:
        g.adno = session['adno']

@app.route('/logout')
def logout():
    #session.pop('adno', None)
    session['adno'] = None
    g.adno = None
    win32api.MessageBox(0, 'Logout Successfully', 'Congratulations', 0x00001000)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)