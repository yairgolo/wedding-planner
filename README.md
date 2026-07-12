# Wedding Planner

מערכת ניהול חתונה בעברית, RTL ו-Mobile First.

## גרסה נוכחית — 0.4.0

הגרסה הנוכחית כוללת:

- Flask Application Factory
- Blueprints
- SQLAlchemy + Flask-Migrate
- Flask-Login ו-password hashing
- CSRF, rate limiting ו-security headers בפרודקשן
- Dashboard בסיסי בעיצוב Olive/Cream/Gold
- תפריט מובייל אמין ו-bottom navigation
- Docker + Gunicorn + Nginx template
- Health endpoint
- pytest + Ruff + GitHub Actions
- בסיס Multi-Wedding להרחבה עתידית
- ניהול מוזמנים ו-RSVP אישי
- מרכז הזמנות ו-WhatsApp עם שיתוף תמונה וטקסט
- מערכת הושבה ויזואלית, Drag & Drop ומצב יום האירוע
- ייצוא Excel למוזמנים ולהושבה

## הרצה מקומית

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
python run.py
```

כניסה לפי `ADMIN_EMAIL` ו-`ADMIN_PASSWORD` שבקובץ `.env`.

## Docker

```bash
cp .env.example .env
docker compose build
docker compose run --rm web flask --app run.py init-db
docker compose up -d
```

האתר יהיה זמין מקומית ב-`http://127.0.0.1:8000`.

## Production

1. להגדיר `FLASK_ENV=production`.
2. להגדיר `SECRET_KEY` ארוך ואקראי.
3. לשנות את פרטי מנהל המערכת.
4. להפעיל מאחורי Nginx ו-HTTPS.
5. לגבות את volume של `instance` ואת `uploads`.

## Roadmap

- Sprint 2: Guests + RSVP
- Sprint 3: Invitations + WhatsApp
- Sprint 4: Seating ✅
- Sprint 5: Shopping + Budget
- Sprint 6: Vendors + Tasks
- Sprint 7: Gifts + Documents
- Sprint 8: Export Center
- Sprint 9: PWA
- Sprint 10: Production hardening and deploy

## Sprint 2 — Guests & RSVP

המערכת כוללת כעת CRUD מלא למוזמנים, משפחות, חיפוש וסינון, קישור RSVP אישי, מעקב שליחת הזמנה וייצוא Excel.

לאחר עדכון מ־Sprint 1 יש להריץ שוב:

```bash
pip install -r requirements.txt
flask --app run.py init-db
```

`init-db` אינו מוחק נתונים קיימים; הוא יוצר את הטבלאות החדשות שחסרות.

## Sprint 3 — הזמנות ו-WhatsApp

לאחר הרצת `init-db`, פתח את `/invitations`:

1. העלה תמונת הזמנה.
2. ערוך את תבנית ההודעה. ניתן להשתמש במשתנים `{name}`, `{couple}`, `{date}`, `{venue}`, `{address}`, `{rsvp_url}`.
3. פתח את האתר באייפון דרך HTTPS.
4. לחץ על "שליחת הזמנה" ובחר WhatsApp בחלון השיתוף.

התמונה מעובדת מראש דרך Canvas ונשלחת כקובץ PNG יחד עם הטקסט וקישור RSVP אישי. השליחה מסומנת רק לאחר שחלון השיתוף הושלם.
