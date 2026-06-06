# MindMate Mental Wellness Tracker

This repository contains the MindMate interactive web app for tracking student mental well-being during exam preparation and result seasons. Students can record daily mood, stress level, sleep and study hours, select stress triggers, and add a short reflection. The app stores entries in a CSV file and uses simple rules to suggest coping strategies and detect crisis phrases. A report endpoint summarises mood distribution and average stress/sleep/study hours.

## Interactive Web App

The interactive version served by `mindmate_webapp.py` uses plain JavaScript to submit check‑in data and retrieve results without page reloads. The root page (`/`) displays a form for daily check-ins. Upon submission, the page shows personalised suggestions and a crisis alert if necessary. A "View report" button fetches and displays summary statistics. API endpoints:

- `POST /api/submit` – Accepts JSON check-in data and returns suggestions.
- `GET /api/report` – Returns JSON summary of all stored check-ins.

## Files
- `mindmate_tool.py` – Core logic for storing check-ins and generating suggestions.
- `mindmate_webapp.py` – HTTP server with interactive client-side UI.
- `requirements.txt` – Specifies `pandas` for CSV handling.
- `Procfile` – Declares the command for Heroku or similar platforms.

## Running Locally

1. Install Python 3.10 or later.
2. Run `pip install -r requirements.txt` to install `pandas`.
3. Start the server: `python mindmate_webapp.py`. By default it runs on port 8000.
4. Open a browser to `http://localhost:8000/` to use the app.

## Deployment

The app uses only the Python standard library and `pandas`, making it easy to deploy. To deploy on Heroku:

```
heroku create mental-wellness-tracker
git init
git add .
git commit -m "Deploy interactive MindMate app"
heroku buildpacks:set heroku/python
git push heroku master
```

Heroku will install dependencies from `requirements.txt` and run the command specified in `Procfile`. After deployment, the app will be available at `https://<app-name>.herokuapp.com/`.

Alternatively, you can deploy on any platform supporting Python web servers and HTTP.

## Notes

- Data is stored in a CSV file in the user’s home directory (`mindmate_data.csv`).
- The suggestions are rule-based and not a substitute for professional mental health care.
