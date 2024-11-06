import sqlite3

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS completed_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        task_name TEXT,
                        time_to_complete INTEGER,
                        difficulty INTEGER
                    )''')
    conn.commit()
    conn.close()
    
def add_completed_task(user_id, task_name, time_to_complete, difficulty):
    init_db() 
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO completed_tasks (user_id, task_name, time_to_complete, difficulty)
                      VALUES (?, ?, ?, ?)''', (user_id, task_name, time_to_complete, difficulty))
    conn.commit()
    conn.close()

def get_statistics(user_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    # Получаем количество выполненных задач и общее время
    cursor.execute('''SELECT COUNT(*), SUM(time_to_complete) FROM completed_tasks WHERE user_id = ?''', (user_id,))
    total_tasks, total_time = cursor.fetchone()
    
    if total_tasks == 0 or total_tasks is None:
        return 0, 0, {'easy': 0, 'medium': 0, 'hard': 0}
    
    # Получаем статистику по сложностям
    cursor.execute('''SELECT difficulty, COUNT(*) FROM completed_tasks WHERE user_id = ? GROUP BY difficulty''', (user_id,))
    rows = cursor.fetchall()
    
    difficulty_stats = {
        'easy': 0,
        'medium': 0,
        'hard': 0
    }
    
    for difficulty, count in rows:
        if difficulty == 1:
            difficulty_stats['easy'] = count
        elif difficulty == 2:
            difficulty_stats['medium'] = count
        elif difficulty == 3:
            difficulty_stats['hard'] = count

    conn.close()
    
    return total_tasks, total_time or 0, difficulty_stats



