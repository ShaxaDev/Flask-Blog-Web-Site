from flaskblog.models import User, Post,PostLike,Code1
from flask import render_template,url_for,flash,redirect,request,abort
from flaskblog.forms import RegistrationForm, LoginForm,  UpdateAccountForm,PostForm,SearchForm,RequestPasswordForm,RequestRestForm
from flaskblog import app,bcrypt,db,admin,mail
from covid import Covid
import secrets
import os
import datetime
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message 

covid = Covid()
k = covid.get_data()

x=datetime.datetime.now()

y='{}-{} {}'.format(x.strftime("%d"), x.strftime("%B"), x.strftime("%Y"))
k = covid.get_status_by_country_name("Uzbekistan")
m=k['confirmed']
m1=k['recovered']
m2=k['deaths']
m3='{} %'.format(int((m1/m)*100))

admin.add_view(ModelView(Code1,db.session))
admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(Post,db.session))
admin.add_view(ModelView(PostLike,db.session))



@app.route('/')
@app.route('/home')
def home():
    
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('index.html',posts=posts,m=m,m1=m1,m2=m2,m3=m3,y=y)

@app.route('/about')
def about():
    return render_template('about.html',m=m, m1=m1, m2=m2, m3=m3,y=y)
@app.route('/register',methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form=RegistrationForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        hashed_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        u=User(email=form.email.data,username=form.username.data,password=hashed_pass)
       

        db.session.add(u)
        db.session.commit()

        flash('Account yaratildi kiring...','success')
        return redirect(url_for('login'))
   
    return render_template('register.html',form=form,m=m,m1=m1,m2=m2,m3=m3)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')


            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:

            flash('Login xato qlyapsiz boshqattan ', 'danger')   
    return render_template('login.html',form=form,m=m,m1=m1,m2=m2,m3=m3,y=y)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex + f_ext
    picture_path=os.path.join(app.root_path,'static/images',picture_fn)
    form_picture.save(picture_path)

    return picture_fn



@app.route('/account',methods=['POST', 'GET'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.img_file=picture_file
            db.session.commit()

        current_user.username=form.username.data 
        current_user.email=form.email.data
        db.session.commit()
        flash('Malumotlaringiz uzgartrildi sucsseeeessss ', 'success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email

    
    return render_template('account.html',form=form,m=m,m1=m1,m2=m2,m3=m3,y=y)

@app.route('/members')
def member():
    page = request.args.get('page', 1, type=int)
    user=User.query.order_by().paginate(page=page,per_page=5)   
    return render_template('member.html',user=user, m=m, m1=m1, m2=m2, m3=m3,y=y)

@app.route('/post',methods=['POST', 'GET'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('post yaratildi','success')
        return redirect(url_for('home'))
    
 

    return render_template('create_post.html', form=form, m=m, m1=m1, m2=m2, m3=m3, y=y,legend='add post')
@app.route('/post/<int:post_id>')
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html', m=m, m1=m1, m2=m2, m3=m3, y=y,post=post)


@app.route('/post/<int:post_id>/update',methods=['POST', 'GET'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('post uzgartrildi kuring ','success')
        return redirect(url_for('post',post_id=post.id))
    
    form.title.data=post.title
    form.content.data=post.content
    return render_template('create_post.html', form=form, m=m, m1=m1, m2=m2, m3=m3, y=y,legend='Update post')

@app.route('/post/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('post o`chirldi!','success')
    return redirect(url_for('home'))


@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
   
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(url_for('home'))




@app.route('/user/<string:username>')
def user(username):
    user=User.query.filter_by(username=username).first_or_404()
    
    page=request.args.get('page',1,type=int)
    posts=Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('count_post.html',posts=posts,m=m,m1=m1,m2=m2,m3=m3,y=y,user=user)
@app.route('/search',methods=['GET','POST'])
def search():    
    look_for = '%{0}%'.format(request.form['qidir'])
    posts = Post.query.filter(Post.title.like(look_for))
    
   
    flash('Qidiruv natijalari', 'success')
    return render_template('search.html',posts=posts,m=m,m1=m1,m2=m2,m3=m3,y=y)
    
@app.route('/searchmember',methods=['GET','POST'])
def searchmember():    
    look_for = '%{0}%'.format(request.form['sasa'])
    posts = User.query.filter(User.username.like(look_for))
    
   
    flash('Qidiruv natijalari', 'success')
    return render_template('searchmember.html',posts=posts,m=m,m1=m1,m2=m2,m3=m3,y=y)

@app.route('/learncode')
def learn():
    page=request.args.get('page',1,type=int)
    url=Code1.query.order_by().paginate(page=page,per_page=2)
    
    
    return render_template('learn.html',url=url,m=m,m1=m1,m2=m2,m3=m3,y=y)