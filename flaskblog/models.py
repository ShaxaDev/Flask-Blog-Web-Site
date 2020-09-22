from datetime import datetime
from flaskblog import db,login_manager,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    img_file=db.Column(db.String(20),nullable=False,default='default.jpg')
    password=db.Column(db.String(60),nullable=False)
    posts=db.relationship('Post',backref='author',lazy=True)
    liked = db.relationship('PostLike',foreign_keys='PostLike.user_id',backref='user', lazy='dynamic')

    def get_reset_token(self,expires_sec=1800):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def  __repr__(self):
        return f"User ('{self.username}','{self.email}','{self.img_file}')"
    
    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id,post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id,PostLike.post_id == post.id).count() > 0

class PostLike(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date_posted=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    
    def  __repr__(self):

        return f"Post ('{self.title}','{self.date_posted}')"
    
class Learn(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url=db.Column(db.String(30),nullable=False)
    title=db.Column(db.Text,nullable=False)
    date_posted=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self):
        return f"Learn('{self.url}','{self.date_posted}')"
class Code(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url=db.Column(db.String(100),nullable=False)
    title=db.Column(db.Text,nullable=False)
    date_posted=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self):
        return f"Code('{self.url}','{self.date_posted}')"

class Code1(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    url=db.Column(db.String(100),nullable=False)
    title=db.Column(db.Text,nullable=False)
    date_posted=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self):
        return f"Code('{self.url}','{self.date_posted}')"
