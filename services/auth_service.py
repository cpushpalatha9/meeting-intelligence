import hashlib, hmac, secrets, sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'database' / 'meetings.db'
DB_PATH.parent.mkdir(exist_ok=True)


def _conn():
    c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init_auth():
    with _conn() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        try:
            c.execute('ALTER TABLE meetings ADD COLUMN owner_id INTEGER')
        except sqlite3.OperationalError:
            pass


def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 200_000).hex()
    return digest, salt


def register_user(name, email, password):
    init_auth()
    name, email = name.strip(), email.strip().lower()
    if not name or not email or len(password) < 6:
        return False, 'Name, email and a password of at least 6 characters are required.'
    digest, salt = _hash_password(password)
    try:
        with _conn() as c:
            c.execute('INSERT INTO users(name,email,password_hash,salt) VALUES(?,?,?,?)', (name,email,digest,salt))
        return True, 'Account created successfully.'
    except sqlite3.IntegrityError:
        return False, 'An account with this email already exists.'


def authenticate(email, password):
    init_auth()
    with _conn() as c:
        row = c.execute('SELECT * FROM users WHERE email=?', (email.strip().lower(),)).fetchone()
    if not row:
        return None
    digest, _ = _hash_password(password, row['salt'])
    if hmac.compare_digest(digest, row['password_hash']):
        return dict(row)
    return None


def get_user(user_id):
    init_auth()
    with _conn() as c:
        row = c.execute('SELECT id,name,email,role,created_at FROM users WHERE id=?', (user_id,)).fetchone()
    return dict(row) if row else None
