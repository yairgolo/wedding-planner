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
- `/invite-manager/admin/login` — כלי עצמאי לשליחת הזמנות

## כלי שליחת הזמנות עצמאי

הכלי יושב על אותו שרת אך מופרד מהאתר הראשי: רשימת מוזמנים, תמונת הזמנה,
קישורי משתמשים וסטטוסים משלו. לאחר משיכת העדכון, הריצו פעם אחת:

```powershell
flask --app run.py init-db
```

ואז פתחו `/invite-manager/admin/login` והיכנסו עם חשבון המנהל הקיים. במסך
"שולחים" יוצרים קישור אישי לכל בן משפחה ומשייכים אותו לצד החתן או הכלה.
כל קישור מציג רק את המוזמנים של הצד שלו. לפני השיתוף יש תצוגה מקדימה, ולאחר
החזרה מ־WhatsApp המשתמש מאשר במפורש שההזמנה אכן נשלחה.

### עדכון פורטל ההזמנות ב־PythonAnywhere

לעדכון זה נוספה טבלת ניסיונות שליחה. חובה להריץ את `init-db` לפני Reload:

```bash
cd ~/wedding-planner
git pull
source .venv/bin/activate
python -m flask --app run.py init-db
```

לאחר הצלחת הפקודה: Web → Reload, ואז רענון העמוד בטלפון.
לא נדרשות חבילות חדשות. הפקודה מוסיפה טבלאות ואינה מוחקת מוזמנים קיימים.

המנהל יכול לשלוח ישירות מהרשימה: בנוסח משותף או בשם שולח מהצד של המוזמן.
כל שולח יכול לערוך את נוסחיו ולהוסיף, לערוך, לייבא ולייצא מוזמנים בצד שלו.
ב־Excel העדכון הוא לפי מזהה בלבד; מזהה לא מוכר, כפול, צד לא מורשה או פנייה חסרה
עוצרים את הייבוא כולו ומציגים דוח לתיקון. שדות היסטוריית השליחה הם לקריאה בלבד.

שיתוף תמונה וטקסט דורש דפדפן תומך ב־HTTPS. האתר פותח את חלון השיתוף של הטלפון;
המשתמש בוחר WhatsApp ונמען. האתר אינו יכול לבחור אוטומטית נמען בשיתוף קובץ.
לחלופין אפשר לפתוח את השיחה לנמען עם טקסט, ולהוריד ולצרף את התמונה ידנית.
חזרה מ־WhatsApp אינה הוכחה לשליחה: רק אישור מפורש מסמן ״נשלח״.
ביטול שליחה חוזרת משמר את סטטוס השליחה הקודם; רענון מאפשר להמשיך ניסיון פתוח.

### בדיקות פורטל ההזמנות

```bash
python -m pytest -q
python -m ruff check .
```

`tests/test_invite_portal.py` בודק הרשאות, צדדים, קישורים, CRUD, תהליך השליחה,
אישורים כפולים, ביטולים, Excel, העלאת תמונות, CSRF וטקסט בלתי מהימן.
לבדיקות דפדפן מקומיות עם נתונים זמניים בלבד:

```bash
PYTHONPATH=. python tests/portal_preview.py
```

ב־PowerShell: הגדירו קודם `$env:PYTHONPATH='.'` ואז `python tests/portal_preview.py`.
בטרמינל נוסף עם Playwright זמין ל־Node:

```bash
node tests/portal_browser.cjs
node tests/portal_browser_https.cjs
```

הבדיקה משתמשת ב־Edge מותקן כברירת מחדל. אפשר לבחור Chrome באמצעות
`PORTAL_BROWSER_CHANNEL=chrome`. היא בודקת רוחבי טלפון ומחשב, לחיצות, שיתוף
מדומה ושגיאות דפדפן. היא אינה שולחת הודעות אמיתיות. חובה לבצע בדיקת קצה בטלפון
של השולח כדי לוודא שגרסת WhatsApp שלו מקבלת את התמונה והטקסט יחד.

בדיקת HTTPS מפעילה את יצירת כותרת Referer בדפדפן ומעבירה את הבקשות לשרת
הבדיקה המקומי דרך כותרות reverse proxy. היא מכסה כניסה, עריכה ושליחה עם
CSRF פעיל, ומוודאת שקישור אישי אינו מועבר לאתר חיצוני. אין תקשורת לדומייני הבדיקה.

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

## Sprint 7 — Gifts, Documents and Activity

New routes:

- `/gifts` — gifts and thank-you tracking
- `/documents` — secure document uploads and downloads
- `/activity` — recent system activity
- `/trash` — restore softly deleted records

## Sprint 8.3 — Excel Round Trip

רשימת המוזמנים ניתנת לייצוא, עריכה וייבוא חוזר:

1. הורד `wedding-guests-roundtrip.xlsx` מעמוד המוזמנים.
2. ערוך רשומות קיימות או הוסף שורות חדשות בגיליון `מוזמנים`.
3. אל תשנה `UUID` או `מזהה מערכת` של רשומות קיימות.
4. העלה את הקובץ דרך `/imports` במצב עדכון.

שדות ריקים כגון טלפון, אימייל, משפחה או שולחן אינם עוצרים את הייבוא. ערכים
שלא ניתן לפרש מקבלים ברירת מחדל ומופיעים בדוח אזהרות לאחר הייבוא.

## Wedding Day Mode

פתחו `/event-day` לקבלת מסך תפעולי לטלפון: חיפוש אורח ושולחן, אנשי קשר של ספקים, לוח זמנים וצ׳קליסט.

## System Health

משתמש מנהל יכול לפתוח `/admin/system` ולבדוק מסד נתונים, הרשאות כתיבה, גרסת Python ומוכנות HTTPS.

## Python

הפרויקט תומך ב-Python 3.10 ומעלה. מומלץ Python 3.12 או 3.13.
