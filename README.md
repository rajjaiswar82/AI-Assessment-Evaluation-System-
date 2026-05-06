# AI Assessment Evaluation System

A complete AI-powered assessment system with web interface, intelligent scoring, and negative marking.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**
   - Install PostgreSQL
   - Create database: `ai_assessment_db`
   - Update `.env` with your database credentials

3. **Run the System**
   ```bash
   python main.py
   ```
   Or double-click: `run_system.bat`

4. **Access Web Interface**
   Open: http://localhost:8000

## 📊 Features

✅ **Web Interface** - Modern, responsive UI  
✅ **AI Evaluation** - Multi-metric scoring (Correctness, Depth, Clarity)  
✅ **Negative Marking** - Intelligent penalty system  
✅ **Real-time Results** - Instant feedback  
✅ **PostgreSQL Database** - Persistent data storage  
✅ **Admin Dashboard** - System management  
✅ **API Documentation** - Auto-generated at /docs  

## 🎯 Usage

### Take Assessment
1. Enter Candidate ID
2. Answer questions
3. Get instant AI evaluation
4. View final results

### View Results
1. Enter Candidate ID
2. See detailed score breakdown
3. Review answer history

### Admin Panel
1. View system statistics
2. Manage questions
3. Access API documentation

## 🛠️ Technology Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Frontend**: HTML/CSS/JavaScript
- **AI Scoring**: Custom algorithms
- **Validation**: Pydantic

## 📁 Project Structure

```
├── main.py              # FastAPI application
├── models.py            # Database models
├── services.py          # Business logic
├── evaluation_engine.py # AI scoring
├── static/              # Web UI files
├── requirements.txt     # Dependencies
└── .env                 # Configuration
```

## ⚙️ Configuration

Edit `.env` file:
```env
DATABASE_URL=
```

## 🎓 Ready for Production

This system is complete and ready for:
- College projects
- Technical assessments
- Online evaluations
- Educational platforms

---

**Version**: 1.0  
**Status**: Production Ready ✅
