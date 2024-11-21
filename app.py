import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

# Function to establish a database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Ensure database.db exists in the project directory
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries for easier access
    return conn

# Function to get a specific post by its ID
def get_post(post_id):
    conn = get_db_connection()  # Open the connection to the database
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()  # Fetch the post
    conn.close()  # Close the connection
    if post is None:  # Check if the post exists
        abort(404)  # Return a 404 error if not found
    return post

# Create a Flask application instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'zxcvbnm'

# Define a view function for the main route '/'
@app.route('/')
def index():
    conn = get_db_connection()  # Establish database connection
    posts = conn.execute('SELECT * FROM posts').fetchall()  # Query all posts from the 'posts' table
    conn.close()  # Close the connection
    return render_template('index.html', posts=posts)  # Render the main page with posts

# Define a view function for a specific post
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)  # Get the post using the helper function
    return render_template('post.html', post=post)  # Render the post page with the post data

# Define a view function for creating a new post
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        # Get the title and content from the form
        title = request.form['title']
        content = request.form['content']

        # Validate that a title is provided
        if not title:
            flash('Title is required!')
        else:
            # Insert the new post into the database
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()

            # Redirect to the main page
            return redirect(url_for('index'))

    return render_template('create.html')  # Render the create post page

# Define a view function for editing a post
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)  # Get the post to be edited by its ID

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Validate that a title is provided
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            # Update the table with the new title and content
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))  # Redirect to the main page after editing

    return render_template('edit.html', post=post)  # Render the edit post page

# Define the delete view function
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)  # Get the post to be deleted
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))  # Delete the post from the database
    conn.commit()
    conn.close()

    flash(f'"{post["title"]}" was successfully deleted!')  # Flash a message on successful deletion
    return redirect(url_for('index'))  # Redirect to the main page after deletion

# Run the application
if __name__ == '__main__':
    app.run(debug=True)

