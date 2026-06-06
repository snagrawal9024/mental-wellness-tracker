"""
MindMate Exam Wellness Web Application

This interactive web app provides an HTML form for students to log daily mood,
stress, sleep, study hours, stress triggers, and a short journal entry. It
responds with personalised wellness suggestions and highlights crisis phrases.
The root path (/) serves the interactive single page app with fetch-based
submission. The /api/submit endpoint accepts POST data and returns JSON, and
/api/report returns aggregated statistics as JSON.
"""
import http.server
import urllib.parse
import datetime
import html
import json
from typing import List

from mindmate_tool import create_check_in, load_data


class MindMateHandler(http.server.SimpleHTTPRequestHandler):
    def _interactive_page(self) -> str:
        # Return HTML for a single-page app. Use fetch to call API.
        return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MindMate Wellness App</title>
<style>
body {font-family: Arial, sans-serif; margin:2em; background:#f7f7f7;}
label {display:block; margin-top:0.5em;}
input[type=text], input[type=number], select, textarea {width:100%; padding:0.5em; margin-top:0.2em;}
textarea {height:4em;}
button {margin-top:1em; padding:0.5em 1em; background:#3498db; color:white; border:none; cursor:pointer;}
#suggestions {margin-top:2em; border:1px solid #ddd; background:white; padding:1em; display:none;}
#suggestions ul {list-style: disc inside;}
#suggestions .alert {color:#c0392b; font-weight:bold;}
#report {margin-top:2em; border:1px solid #ddd; background:white; padding:1em; display:none;}
</style>
</head>
<body>
<h1>MindMate Daily Check-In</h1>
<form id="checkin">
<label>Name:<br><input type="text" name="name" required></label>
<label>Exam type (e.g., NEET, JEE, Board):<br><input type="text" name="exam" required></label>
<label>Mood:<br>
<select name="mood" required>
<option value="Happy">Happy</option>
<option value="Calm">Calm</option>
<option value="Sad">Sad</option>
<option value="Angry">Angry</option>
<option value="Anxious">Anxious</option>
<option value="Tired">Tired</option>
</select>
</label>
<label>Stress level (1–10):<br><input type="number" name="stress" min="1" max="10" required></label>
<label>Sleep hours (last night):<br><input type="number" name="sleep" step="0.1" min="0" required></label>
<label>Study hours (today):<br><input type="number" name="study" step="0.1" min="0" required></label>
<label>Stress triggers (comma separated):<br><input type="text" name="triggers"></label>
<label>Reflection / Journal:<br><textarea name="journal"></textarea></label>
<button type="submit">Submit</button>
</form>
<div id="suggestions">
<div class="alert" id="alert"></div>
<h2>Personalised suggestions</h2>
<ul id="suggestList"></ul>
</div>
<button id="viewReport">View report</button>
<div id="report"></div>
<script>
const form = document.getElementById('checkin');
form.addEventListener('submit', function(ev) {
  ev.preventDefault();
  const data = new FormData(form);
  document.getElementById('suggestList').innerHTML = '';
  document.getElementById('alert').textContent = '';
  fetch('/api/submit', {method:'POST', body:data})
    .then(resp => resp.json())
    .then(obj => {
      if (obj.suggestions && obj.suggestions.length) {
        obj.suggestions.forEach(function(s) {
          const li = document.createElement('li');
          li.textContent = s;
          document.getElementById('suggestList').appendChild(li);
        });
      } else {
        const li = document.createElement('li');
        li.textContent = 'No specific suggestions today. Keep taking care of yourself!';
        document.getElementById('suggestList').appendChild(li);
      }
      if (obj.crisis) {
        document.getElementById('alert').textContent = 'Crisis alert: your entry contains phrases that may indicate severe distress. Please reach out to a trusted adult, counsellor or hotline.';
      }
      document.getElementById('suggestions').style.display = 'block';
      form.reset();
    });
});
document.getElementById('viewReport').addEventListener('click', function() {
  fetch('/api/report').then(resp => resp.json()).then(data => {
    const div = document.getElementById('report');
    if (data.total === 0) {
      div.innerHTML = '<p>No data available. Start by adding some check-ins.</p>';
    } else {
      let html = '<p>Total check-ins: ' + data.total + '</p>';
      html += '<p><strong>Mood distribution:</strong></p><ul>';
      for (const mood in data.mood_counts) {
        html += '<li>' + mood + ': ' + data.mood_counts[mood] + '</li>';
      }
      html += '</ul>';
      html += '<p>Average stress level: ' + data.avg_stress.toFixed(2) + '</p>';
      html += '<p>Average sleep hours: ' + data.avg_sleep.toFixed(2) + '</p>';
      html += '<p>Average study hours: ' + data.avg_study.toFixed(2) + '</p>';
      div.innerHTML = html;
    }
    div.style.display = 'block';
  });
});
</script>
</body>
</html>"""

    def do_GET(self):
        if self.path in ('/', '/index', '/index.html', '/app'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            page = self._interactive_page()
            self.wfile.write(page.encode('utf-8'))
        elif self.path == '/api/report':
            df = load_data()
            if df is None or df.empty:
                data = {"total": 0, "mood_counts": {}, "avg_stress": 0.0, "avg_sleep": 0.0, "avg_study": 0.0}
            else:
                total = int(len(df))
                mood_counts = df['mood'].value_counts().to_dict()
                avg_stress = float(df['stress'].mean())
                avg_sleep = float(df['sleep_hours'].mean())
                avg_study = float(df['study_hours'].mean())
                data = {"total": total, "mood_counts": mood_counts, "avg_stress": avg_stress,
                        "avg_sleep": avg_sleep, "avg_study": avg_study}
            resp = json.dumps(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(resp.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/submit':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            params = urllib.parse.parse_qs(body)
            get = lambda k: params.get(k, [''])[0]
            name = get('name').strip()
            exam = get('exam').strip()
            mood = get('mood').strip()
            stress = int(get('stress') or 0)
            sleep_hours = float(get('sleep') or 0)
            study_hours = float(get('study') or 0)
            triggers_raw = get('triggers')
            triggers = [t.strip() for t in triggers_raw.split(',')] if triggers_raw else []
            journal = get('journal').strip()
            _, suggestions, crisis = create_check_in(
                name=name,
                exam=exam,
                mood=mood,
                stress=stress,
                sleep_hours=sleep_hours,
                study_hours=study_hours,
                triggers=triggers,
                journal=journal,
                date=datetime.date.today(),
                store=True,
            )
            data = {'suggestions': suggestions, 'crisis': crisis}
            resp = json.dumps(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(resp.encode('utf-8'))
        else:
            super().do_POST()


def run_server(port: int = 8000):
    server_address = ('', port)
    with http.server.ThreadingHTTPServer(server_address, MindMateHandler) as httpd:
        print(f'Serving MindMate web app on port {port}...')
        httpd.serve_forever()


if __name__ == '__main__':
    run_server()
