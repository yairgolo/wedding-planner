# פריסה חינמית ללא דומיין — PythonAnywhere

המסלול הזה מתאים לגרסת החתונה הנוכחית משום שהוא נותן:

- כתובת HTTPS חינמית: `https://USERNAME.pythonanywhere.com`
- אחסון קבצים קבוע עבור SQLite, תמונת ההזמנה ומסמכים
- אין צורך לקנות דומיין
- אין צורך להפעיל מחשב בבית

## 1. פתיחת חשבון

פתח חשבון Beginner חינמי ב-PythonAnywhere.

## 2. העלאת הקוד

פתח Bash Console והרץ:

```bash
git clone https://github.com/yairgolo/wedding-planner.git
cd wedding-planner
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

אם Python 3.13 לא זמין בחשבון, השתמש ב-3.12 או 3.11.

## 3. קובץ סביבה

```bash
cp .env.pythonanywhere.example .env
nano .env
```

החלף:

- `YOUR_USERNAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `SECRET_KEY`

ליצירת SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 4. יצירת מסד הנתונים

```bash
source .venv/bin/activate
flask --app run.py init-db
```

## 5. יצירת Web App

בלשונית Web:

1. לחץ `Add a new web app`.
2. בחר `Manual configuration`.
3. בחר אותה גרסת Python שבה יצרת את ה-venv.
4. בשדה Virtualenv הכנס:

```text
/home/YOUR_USERNAME/wedding-planner/.venv
```

## 6. WSGI

פתח את קובץ ה-WSGI שנוצר והחלף את תוכנו ב:

```python
import os
import sys

project = "/home/YOUR_USERNAME/wedding-planner"
if project not in sys.path:
    sys.path.insert(0, project)

os.chdir(project)
os.environ.setdefault("FLASK_ENV", "production")

from app import create_app
application = create_app("production")
```

## 7. Static files

בלשונית Web, תחת Static files:

| URL | Directory |
|---|---|
| `/static/` | `/home/YOUR_USERNAME/wedding-planner/app/static/` |

## 8. Reload

לחץ `Reload`.

האתר יהיה זמין ב:

```text
https://YOUR_USERNAME.pythonanywhere.com
```

## 9. עדכון גרסה בעתיד

```bash
cd ~/wedding-planner
git pull
source .venv/bin/activate
pip install -r requirements.txt
flask --app run.py init-db
```

לאחר מכן לחץ Reload בלשונית Web.

## 10. גיבוי ידני

```bash
cd ~/wedding-planner
source .venv/bin/activate
python scripts/backup_local_data.py
```

קובץ ZIP ייווצר בתיקיית `backups`.

## מגבלות המסלול החינמי

- אחסון פרטי מוגבל, לכן לא להעלות סרטונים או קבצים כבדים.
- עובד Worker אחד; למערכת זוגית קטנה זה בדרך כלל מספיק.
- אין Scheduled Tasks בחשבון החינמי, ולכן הגיבוי ידני.
- גישה החוצה מהשרת מוגבלת, אך שיתוף WhatsApp מתבצע בדפדפן ולכן אינו תלוי בכך.
