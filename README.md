# MediQueue — Healthcare Appointment Website

A **beginner-friendly Django** educational prototype with a polished medical website interface inspired by healthcare service websites (not affiliated with Medicare or any insurer).

## Features
- Responsive homepage with medical services and specialty navigation
- Patient registration/login using Django authentication
- Search doctors by specialty and view available times
- Book appointments, cancel future bookings, and reschedule to another free time with the same doctor
- Cancelled appointments remain in history, while their slots become bookable again
- Doctor dashboard: reschedule bookings and complete visits
- Patient profile with phone and insurance plan selection
- Insurance information page with clearly labeled sample coverage notes
- AJAX assistant: `fetch` + Django endpoint + `scikit-learn` TF-IDF similarity for specialty suggestions (not medical diagnosis)
- Django Admin for doctors, specialties, insurance plans, and slots
- Sample content generator (`seed_demo`) to make the site look populated immediately

## Start in VS Code (Windows / Git Bash)
```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py makemigrations clinic
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/ . PowerShell activation: `venv\Scripts\Activate.ps1`.

## Try it
1. Run `seed_demo`, then visit the homepage and Find a Doctor page.
2. Register as a patient; select an example insurance plan.
3. Book a free time slot; visit My Appointments.
4. For doctor login, go to `/admin/`, open Users, select `dr_sara`, set a password through the admin password-change form, then log in as `dr_sara`. Doctor demo accounts are **disabled for password login until you explicitly set passwords**.
5. Doctor Area lets the doctor move an existing booking to another free slot or mark it completed.
6. In Find a Doctor, type `I need a knee specialist` in the AI assistant. It sends an AJAX POST to `/ai/suggest/`.

## Code map (for presentation)
- `clinic/models.py` — database tables and relationships
- `clinic/views.py` — pages and actions
- `clinic/urls.py` — URL to view mapping
- `clinic/forms.py` — registration and patient profile forms
- `clinic/ai_assistant.py` — simple TF-IDF text matching using scikit-learn
- `templates/` — HTML pages
- `static/css/site.css` — styling
- `clinic/management/commands/seed_demo.py` — sample content

## Database relationships
`User 1:1 PatientProfile`; `Insurance 1:N PatientProfile`; `User 1:1 Doctor`; `Specialty 1:N Doctor`; `Doctor 1:N Slot`; `Slot 1:0..1 Appointment`; `User 1:N Appointment`.

## GitHub
```bash
git init
git add .
git commit -m "Build MediQueue healthcare booking website"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/MediQueue.git
git push -u origin main
```

## Safety and limitations
Educational prototype only. Not a medical record system. The assistant matches keywords/statistical text similarity, not a medical diagnosis or conversational LLM. Insurance data is illustrative, not verified insurer eligibility. No live queue, live insurance APIs, or real email sending. Doctor accounts created by the demo seed cannot log in until you assign a password in admin. Do not deploy with the default development secret key or DEBUG enabled. Do not enter real patient data in this demo.

## Cancellation and patient rescheduling
- In **My Appointments**, patients can cancel or reschedule a future booked appointment.
- Cancellation changes the status to `cancelled` (does not delete history).
- Cancelled slots can be booked again; the database prevents more than one active booking per slot.
- Rescheduling is restricted to available slots with the same doctor.
- These actions use POST + CSRF and verify that the logged-in patient owns the appointment.
- For an existing SQLite database from the previous version, back it up first, then run `python manage.py makemigrations clinic` and `python manage.py migrate`.
