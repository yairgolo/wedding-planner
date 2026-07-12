# Wedding Planner

מערכת ניהול חתונה בעברית, RTL ו־Mobile First.

## גרסה 0.5.0 — Sprint 5

המערכת כוללת כעת:

- ניהול מוזמנים, משפחות ו־RSVP אישי
- מרכז הזמנות ו־WhatsApp עם תמונה, טקסט וקישור אישי
- מערכת הושבה עם Drag & Drop ומצב יום האירוע
- ניהול קניות לחתונה, לבית ולכללי
- Wishlist, עדיפות, קישורי מוצר, מחירים ותאריכי יעד
- תקציב יעד, התחייבויות, תשלומים ויתרות
- ייצוא Excel מעוצב למוזמנים, הושבה, קניות ותקציב
- ייצוא טקסט מסודר ל־WhatsApp לקניות ולתקציב
- Dashboard מותאם לנייד
- Flask Factory, SQLAlchemy, Flask-Login, CSRF ו־ProxyFix
- Docker, Gunicorn, Nginx, pytest ו־Ruff

## הרצה מקומית ב־Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app run.py init-db
python run.py
```

פתחו בדפדפן:

```text
http://127.0.0.1:5000
```

פרטי הכניסה נקבעים בקובץ `.env` באמצעות:

```env
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-now
```

## שדרוג מספרינט קודם

חלצו את הקבצים מעל הפרויקט הקיים והריצו:

```powershell
pip install -r requirements.txt
flask --app run.py init-db
python run.py
```

`init-db` יוצר את הטבלאות החדשות ואינו מוחק את הנתונים הקיימים.

## Docker

```bash
cp .env.example .env
docker compose build
docker compose run --rm web flask --app run.py init-db
docker compose up -d
```

## בדיקות

```bash
pytest -q
ruff check .
```

## הנתיבים העיקריים

- `/guests` — מוזמנים
- `/invitations` — הזמנות ו־WhatsApp
- `/seating` — הושבה
- `/shopping` — קניות
- `/budget` — תקציב ותשלומים

## Sprint 6 — Vendors & Tasks

- ניהול ספקים, חוזים, תשלומים, פרטי קשר ושעות הגעה.
- ניהול משימות בתצוגת Kanban עם אחריות, עדיפות ותאריך יעד.
- ייצוא Excel וטקסט WhatsApp לשני המודולים.

## Roadmap

- Sprint 6: ספקים, משימות ולוח זמנים
- Sprint 7: מתנות ומסמכים
- Sprint 8: מרכז ייצוא מלא
- Sprint 9: PWA והרשאות מרובות משתמשים
- Sprint 10: Production hardening ו־Deploy
