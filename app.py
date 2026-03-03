from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'rising-sun-blog-secret-key-2024'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False, default='Rising Sun')
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(50), nullable=False, default='General')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    featured = db.Column(db.Boolean, default=False)

    def get_preview(self):
        return self.excerpt or self.content[:150] + '...'

    def get_formatted_date(self):
        return self.created_at.strftime('%B %d, %Y')

# Create database tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    featured_posts = BlogPost.query.filter_by(featured=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=6)
    return render_template("index.html", featured_posts=featured_posts, posts=posts)

@app.route("/post/<int:post_id>")
def view_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    related_posts = BlogPost.query.filter_by(category=post.category).filter(BlogPost.id != post_id).limit(3).all()
    return render_template("post.html", post=post, related_posts=related_posts)

@app.route("/create", methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author', 'Rising Sun')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        category = request.form.get('category', 'General')
        featured = request.form.get('featured') == 'on'

        if not title or not content:
            flash('Title and content are required!', 'error')
            return redirect(url_for('create_post'))

        post = BlogPost(
            title=title,
            author=author,
            content=content,
            excerpt=excerpt,
            category=category,
            featured=featured
        )
        db.session.add(post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('view_post', post_id=post.id))

    categories = ['General', 'Technology', 'Travel', 'Lifestyle', 'Business', 'Health']
    return render_template("create.html", categories=categories)

@app.route("/edit/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.author = request.form.get('author')
        post.content = request.form.get('content')
        post.excerpt = request.form.get('excerpt')
        post.category = request.form.get('category')
        post.featured = request.form.get('featured') == 'on'
        post.updated_at = datetime.now()

        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('view_post', post_id=post.id))

    categories = ['General', 'Technology', 'Travel', 'Lifestyle', 'Business', 'Health']
    return render_template("edit.html", post=post, categories=categories)

@app.route("/delete/<int:post_id>", methods=['POST'])
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route("/category/<category>")
def view_category(category):
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(category=category).order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=6)
    return render_template("category.html", category=category, posts=posts)

@app.route("/search")
def search():
    query = request.args.get('q', '')
    if query:
        posts = BlogPost.query.filter(
            (BlogPost.title.ilike(f'%{query}%')) | 
            (BlogPost.content.ilike(f'%{query}%'))
        ).order_by(BlogPost.created_at.desc()).all()
    else:
        posts = []
    return render_template("search.html", query=query, posts=posts)

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)