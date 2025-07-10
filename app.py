import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from datetime import datetime
import os
import threading
import webview

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Create folders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#667eea',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create todos table with folder_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            priority TEXT DEFAULT 'medium',
            category TEXT DEFAULT 'general',
            folder_id INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE SET NULL
        )
    ''')
    
    # Insert default folder if none exists
    cursor.execute('SELECT COUNT(*) FROM folders')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO folders (name, color) VALUES (?, ?)', ('General', '#667eea'))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

# API Routes for Folders
@app.route('/api/folders', methods=['GET'])
def get_folders():
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.id, f.name, f.color, f.created_at, COUNT(t.id) as todo_count
        FROM folders f
        LEFT JOIN todos t ON f.id = t.folder_id
        GROUP BY f.id
        ORDER BY f.created_at ASC
    ''')
    
    folders = []
    for row in cursor.fetchall():
        folder_id = row[0]
        # Obtener cantidad de tareas completadas para este folder
        cursor2 = conn.cursor()
        cursor2.execute('SELECT COUNT(*) FROM todos WHERE folder_id = ? AND completed = 1', (folder_id,))
        completed_count = cursor2.fetchone()[0]
        folders.append({
            'id': row[0],
            'name': row[1],
            'color': row[2],
            'created_at': row[3],
            'todo_count': row[4],
            'completed_count': completed_count
        })
    
    conn.close()
    return jsonify(folders)

@app.route('/api/folders', methods=['POST'])
def create_folder():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Folder name is required'}), 400
    
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO folders (name, color)
        VALUES (?, ?)
    ''', (
        data['name'],
        data.get('color', '#667eea')
    ))
    
    folder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': folder_id, 'message': 'Folder created successfully'}), 201

@app.route('/api/folders/<int:folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Check if folder exists
    cursor.execute('SELECT * FROM folders WHERE id = ?', (folder_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Folder not found'}), 404
    
    # Delete all todos in this folder first
    cursor.execute('DELETE FROM todos WHERE folder_id = ?', (folder_id,))
    
    # Delete the folder
    cursor.execute('DELETE FROM folders WHERE id = ?', (folder_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Folder and all its tasks deleted successfully'})

# API Routes for Todos
@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Get query parameters
    filter_status = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', 'all')
    folder_filter = request.args.get('folder', 'all')
    
    # Build query with JOIN to get folder information
    query = """
        SELECT t.id, t.title, t.description, t.completed, t.priority, 
               t.category, t.folder_id, t.created_at, t.updated_at,
               f.name as folder_name, f.color as folder_color
        FROM todos t
        LEFT JOIN folders f ON t.folder_id = f.id
        WHERE 1=1
    """
    params = []
    
    if filter_status == 'completed':
        query += " AND t.completed = 1"
    elif filter_status == 'pending':
        query += " AND t.completed = 0"
    
    if search_query:
        query += " AND (t.title LIKE ? OR t.description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    
    if category_filter != 'all':
        query += " AND t.category = ?"
        params.append(category_filter)
    
    if folder_filter != 'all':
        query += " AND t.folder_id = ?"
        params.append(folder_filter)
    
    query += " ORDER BY t.created_at DESC"
    
    cursor.execute(query, params)
    todos = cursor.fetchall()
    
    # Convert to list of dictionaries
    todos_list = []
    for todo in todos:
        todos_list.append({
            'id': todo[0],
            'title': todo[1],
            'description': todo[2],
            'completed': bool(todo[3]),
            'priority': todo[4],
            'category': todo[5],
            'folder_id': todo[6],
            'created_at': todo[7],
            'updated_at': todo[8],
            'folder_name': todo[9] or 'General',
            'folder_color': todo[10] or '#667eea'
        })
    
    conn.close()
    return jsonify(todos_list)

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO todos (title, description, priority, category, folder_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['title'],
        data.get('description', ''),
        data.get('priority', 'medium'),
        data.get('category', 'general'),
        data.get('folder_id', 1)  # Default to General folder
    ))
    
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': todo_id, 'message': 'Todo created successfully'}), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    
    # Update todo
    update_fields = []
    params = []
    
    if 'title' in data:
        update_fields.append('title = ?')
        params.append(data['title'])
    
    if 'description' in data:
        update_fields.append('description = ?')
        params.append(data['description'])
    
    if 'completed' in data:
        update_fields.append('completed = ?')
        params.append(data['completed'])
    
    if 'priority' in data:
        update_fields.append('priority = ?')
        params.append(data['priority'])
    
    if 'category' in data:
        update_fields.append('category = ?')
        params.append(data['category'])
    
    if 'folder_id' in data:
        update_fields.append('folder_id = ?')
        params.append(data['folder_id'])
    
    update_fields.append('updated_at = CURRENT_TIMESTAMP')
    params.append(todo_id)
    
    query = f"UPDATE todos SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Todo updated successfully'})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Todo deleted successfully'})

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PUT'])
def toggle_todo(todo_id):
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT completed FROM todos WHERE id = ?', (todo_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    
    # Toggle completed status
    new_status = not result[0]
    cursor.execute('''
        UPDATE todos 
        SET completed = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (new_status, todo_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'completed': new_status, 'message': 'Todo toggled successfully'})

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('todos.db')
    cursor = conn.cursor()
    
    # Get total todos
    cursor.execute('SELECT COUNT(*) FROM todos')
    total = cursor.fetchone()[0]
    
    # Get completed todos
    cursor.execute('SELECT COUNT(*) FROM todos WHERE completed = 1')
    completed = cursor.fetchone()[0]
    
    # Get pending todos
    cursor.execute('SELECT COUNT(*) FROM todos WHERE completed = 0')
    pending = cursor.fetchone()[0]
    
    # Get todos by priority
    cursor.execute('SELECT priority, COUNT(*) FROM todos GROUP BY priority')
    priority_stats = dict(cursor.fetchall())
    
    # Get todos by category
    cursor.execute('SELECT category, COUNT(*) FROM todos GROUP BY category')
    category_stats = dict(cursor.fetchall())
    
    # Get todos by folder
    cursor.execute('''
        SELECT f.name, COUNT(t.id) 
        FROM folders f 
        LEFT JOIN todos t ON f.id = t.folder_id 
        GROUP BY f.id
    ''')
    folder_stats = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending,
        'priority_stats': priority_stats,
        'category_stats': category_stats,
        'folder_stats': folder_stats
    })

def start_flask():
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    import time
    time.sleep(1)

    webview.create_window("TaskMaster", "http://127.0.0.1:5000", width=1100, height=800)
    webview.start(gui='edgechromium') 