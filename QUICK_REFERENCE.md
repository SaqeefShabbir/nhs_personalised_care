# NHS Personalised Care - Quick Reference

## 🏠 Dashboard
- View PAM score and health overview
- Track goals, outcomes, and decisions
- Monitor risk assessment

## 👤 Patients
- `+ New Patient` - Register new patient
- `Select` - Switch between patients

## 🎯 Goals
- `+ New Goal` - Create health goal
- Filter by status (All/Planned/In Progress/Achieved)
- Edit goals to update status

## 📈 Outcomes
- `+ Record Outcome` - Log health metric
- Track progress against targets
- View achievement status

## 🧠 Insights
- `Refresh` - Generate AI predictions
- View risk assessment
- See health recommendations

## 📝 Notes
- `+ Add Note` - Document clinical observations
- Automatic sentiment analysis
- View note history

## ⚙️ Settings
- Switch patients
- Export data (JSON)
- Clear data

## 🛠️ API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/health | GET | Health check |
| /api/person/{nhs} | GET | Get patient |
| /api/goals/{id} | GET | Get goals |
| /api/outcome | POST | Record outcome |
| /api/pam | POST | Record PAM |
| /api/note | POST | Add note |
| /api/insights/{id} | GET | Get insights |