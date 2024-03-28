from flask import Flask,render_template,request,redirect,url_for,flash,session
import mysql.connector
from cmail import sendmail
from otp import genotp
app=Flask(__name__)
app.config['SECRET_KEY']='my super secret key that no one is supported to know'
mydb=mysql.connector.connect(host="localhost",user="root",password="system",db="blog")
with mysql.connector.connect(host="localhost",user="root",password="system",db="blog"):
    cursor=mydb.cursor(buffered=True)
    cursor.execute("create table if not exists reg(name varchar(20) primary key,mobile varchar(20) unique,email varchar(50) unique,address varchar(50),password varchar(20))")
@app.route("/regform",methods=["GET","POST"])
def frm():
    if request.method=="POST":
        name=request.form.get('name')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        address=request.form.get('address')
        password=request.form.get('password')
        otp=genotp()
        sendmail(to=email,subject='THANK YOU for Registration',body=f'otp is : {otp}')
        return render_template('verify.html',name=name,mobile=mobile,email=email,address=address,password=password,otp=otp)
    return render_template("regform.html")
@app.route('/otp/<name>/<mobile>/<email>/<address>/<password>/<otp>',methods=['GET','POST'])
def otp(name,mobile,email,address,password,otp):
    if request.method=='POST':
        uotp=request.form['uotp']
        if otp==uotp:
            cursor=mydb.cursor(buffered=True)
            cursor.execute("insert into reg values(%s,%s,%s,%s,%s)",[name,mobile,email,address,password])
            mydb.commit()
            cursor.close()  
            return redirect(url_for('login'))
    return render_template('verify.html',name=name,mobile=mobile,email=email,address=address,password=password,otp=otp)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        name=request.form.get('name')
        password=request.form.get('password')
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select count(*) from reg where name=%s && password=%s",[name,password])
        data=cursor.fetchone()[0]
        if data==1:
            session['username']=name
            if not session.get(session['username']):
                session[session['username']]={}
            return redirect(url_for('home'))
        else:
            return 'Invalid username and password'
    return render_template('login.html')
@app.route('/logout',methods=['GET','POST'])
def logout():
    if session.get('username'):
        session.pop('username')
    return redirect(url_for('login'))
@app.route('/')
def home():
    return render_template('homepage.html')
@app.route('/post',methods=['GET','POST'])
def post():
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute("insert into posts (title,content,slug) values(%s,%s,%s)",(title,content,slug))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_posts'))
    return render_template('post.html')
@app.route('/admin')
def admin():
    return render_template('hpmepage.html')
@app.route('/view_posts')
def view_posts():
    cursor=mydb.cursor(buffered=True)
    cursor.execute("select * from posts")
    posts=cursor.fetchall()
    print(posts)
    cursor.close()
    return render_template('view_posts.html',posts=posts)
@app.route('/delete/<int:id>',methods=['GET','POST'])
def delete(id):
    cursor=mydb.cursor(buffered=True)
    cursor.execute("select * from posts where id=%s",(id,))
    posts=cursor.fetchone()
    cursor.execute("delete from posts where id=%s",(id,))
    mydb.commit()
    cursor.close()
    return redirect(url_for('view_posts'))
@app.route('/update_post/<int:id>',methods=['GET','POST'])
def update_post(id):
    if request.method=='POST':
        title=request.form['title']
        content=request.form['content']
        slug=request.form['slug']
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select * from posts where id=%s",(id,))
        posts=cursor.fetchone()
        cursor.execute("update posts set title=%s,content=%s,slug=%s where id=%s",(title,content,slug,id))
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_posts'))
    else: 
        cursor=mydb.cursor(buffered=True)
        cursor.execute("select * from posts where id=%s",(id,))
        post=cursor.fetchone()
        cursor.close()
        return render_template('update.html',post=post)
app.run(debug=True,use_reloader=True)