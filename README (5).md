# HCST Elora - The Art of a Connected Campus

A Streamlit web app for Hindustan College of Science and Technology, Farah, Mathura.

- **Campus Directory**: find any office, department or facility by building, floor and room number.
- **Reach HCST**: Google Maps directions from your current location (or any place you type) to the college.
- Visitor Help Centre, Ask HCST chat assistant, Faculty Directory, Appointment booking, Events, Lost & Found.
- User sign-up / login and an Admin panel.

All room numbers, timings and faculty details are **sample data**. Edit `LOC_SEED` in `app.py`
or use **Admin > Places** to correct them.

## Deploy (no local install)
1. Create a GitHub repo and create/upload `app.py`, `requirements.txt`, `README.md`, `.gitignore`
   and `.streamlit/config.toml` (type that exact name in "Create new file").
2. Go to https://share.streamlit.io > Create app > pick the repo, branch `main`, main file `app.py` > Deploy.
3. Optional: in app Settings > Secrets add `ADMIN_PASSWORD = "your-strong-password"` (default is `admin123`).

Note: the SQLite database resets when Streamlit Cloud restarts the app.
