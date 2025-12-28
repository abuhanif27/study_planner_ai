# Copilot Instructions for Fuzzy-GA Study Schedule Generator

## Project Overview

A personalized study schedule optimizer combining **Fuzzy Logic** (stress modeling) and **Genetic Algorithm** (schedule optimization). Three deployment interfaces: Flask web UI (primary), desktop Tkinter GUI, and CLI.

**Key architectural insight:** The system decouples stress computation from schedule generation—Fuzzy Logic calculates daily stress independently; GA uses this to score fitness.

---

## Architecture & Data Flow

### **Component 1: Fuzzy Stress Calculator** (`FuzzyStressCalculator` class)
- **Purpose:** Convert course difficulty + study hours → stress level (0-1)
- **Input:** Daily study hours, average course difficulty
- **Process:** Fuzzify → Apply 7 fuzzy rules → Defuzzify using Center of Gravity
- **Output:** Stress score (0=low, 0.5=medium, 0.8=high)
- **Key rule:** Low hours + high difficulty = high stress (time pressure penalty)

### **Component 2: Genetic Algorithm** (`StudyScheduleGA` class)
- **Chromosome:** Array of length `days × slots_per_day` containing course IDs or 0 (rest)
- **Fitness function:** `α·coverage - β·overload_penalty - γ·stress_penalty` (α=5, β=2, γ=3)
  - **Coverage:** Courses with ≥1 study slot
  - **Overload penalty:** Hours exceeding max per day (squared)
  - **Stress penalty:** Sum of daily stress scores
- **Constraints:** 
  - Daily study hours ≤ `max_hours_per_day` (default 4)
  - Each slot = 1.5 hours
- **Operators:** Tournament selection (size 3), single-point crossover, bit-flip mutation

### **Component 3: Flask Web UI** (`app.py`)
- **Routes:** 
  - `GET /` → Render Material Design HTML
  - `POST /api/courses` → Validate & echo course data
  - `POST /api/generate` → Run GA, return schedule + fitness history
  - `POST /api/export-pdf` → Generate PDF with ReportLab
- **Key pattern:** Request validation happens on backend, not frontend
- **State management:** Results cached in `results_cache` dict; generation updates in `generation_updates`

### **Frontend Architecture** (`templates/index.html`, `static/style.css`, `static/script.js`)
- Material Design with Gradient backgrounds
- Real-time course list & parameter sliders
- Fetch-based API calls with toast notifications
- Results display: Table layout for schedule + chart for fitness history

---

## Critical Workflows

### **Running the Project**

```bash
# Option 1: Web UI (recommended) - see http://localhost:5000
python app.py

# Option 2: Desktop GUI
python fuzzy_ga_study_planner_gui.py

# Option 3: CLI (minimal output)
python fuzzy_ga_study_planner.py
```

### **Typical GA Tuning Parameters**
- **Population Size:** 50-100 (trade-off: larger = better solutions but slower)
- **Generations:** 100-150 (more = better convergence)
- **Days:** 3-7 (planning window)
- **Slots per Day:** 3-4 (study periods)
- **Max Hours/Day:** 4-6 (burnout prevention)

### **Development Workflow**
1. Core algorithm changes → Edit `fuzzy_ga_study_planner.py`
2. Both GUI + Web → Edit `fuzzy_ga_study_planner_gui.py` (imported by `app.py`)
3. Web-only UI changes → Edit `templates/index.html`, `static/style.css`, `static/script.js`
4. Test with `python app.py` (supports live development on port 5000)

---

## Conventions & Patterns

### **Class Design**
- **No inheritance:** `FuzzyStressCalculator` and `StudyScheduleGA` are independent, composed together
- **Method naming:** `calculate_stress()`, `evaluate_fitness()`, `schedule_to_readable()`—all public, no private prefix convention
- **Configuration in `__init__`:** Course data, GA parameters (days, slots, max_hours) passed at instantiation

### **Course Data Structure**
```python
{
    'id': int (1-indexed),
    'name': str,
    'difficulty': int (1-5),
    'exam_days_away': int (1-365)
}
```

### **Fitness Scoring**
- Always non-negative (see `max(0, fitness)` in evaluate_fitness)
- Weights are fixed (α=5, β=2, γ=3)—change in `evaluate_fitness()` method if tuning needed
- Stress penalty is sum of daily stresses; coverage is count of unique courses scheduled

### **Validation Patterns**
- **Input validation:** In `app.py` routes, validates name length, difficulty range, exam days range
- **Constraint validation:** `is_valid_chromosome()` checks daily hour limits
- **No null/None checks in core GA:** Assumes valid input (validation responsibility of Flask layer)

### **Error Handling**
- Flask: Returns JSON with `{'success': False, 'errors': []}` or `{'success': False, 'error': 'message'}`
- GA: No explicit error handling; crashes if invalid data (expected to be caught by validation layer)
- Frontend: Toast notifications for errors, no try-catch blocks needed in JS (async/await)

---

## External Dependencies & Integration

### **Python Packages** (see `requirements.txt`)
- **flask==3.0.0:** Web framework
- **numpy==2.4.0:** Numeric arrays (population, chromosome operations)
- **reportlab==4.4.7:** PDF export (installed but version not in requirements.txt—fix if needed)
- **pygubu, PySimpleGUI:** Desktop GUI (separate from web)

### **Key Integration Points**
1. **Web ↔ GA:** `app.py` imports `FuzzyStressCalculator`, `StudyScheduleGA` from GUI module
2. **PDF Export:** Uses ReportLab to generate PDF from schedule JSON (embedded in POST body)
3. **Frontend ↔ Backend:** Fetch API, JSON bodies, no session/auth (stateless)

### **Browser Compatibility**
- Modern browsers only (Fetch API, ES6)
- No IE11 support (Material Design)

---

## File Map (Key Files)

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `fuzzy_ga_study_planner.py` | Core algorithm (CLI) | `FuzzyStressCalculator`, `StudyScheduleGA` |
| `fuzzy_ga_study_planner_gui.py` | Same as above + Tkinter GUI | Same classes |
| `app.py` | Flask backend, PDF export | Routes: `/api/courses`, `/api/generate`, `/api/export-pdf` |
| `templates/index.html` | HTML structure | Form inputs, result table, canvas for chart |
| `static/style.css` | Material Design styling | Gradients, animations, color scheme |
| `static/script.js` | Frontend interactivity | Fetch calls, form validation, chart rendering |

---

## Common Modifications

### **Add a New Fuzzy Rule**
1. Find `apply_fuzzy_rules()` in `FuzzyStressCalculator`
2. Add new rule as: `stress_mf['target'] += min(hours_mf['x'], difficulty_mf['y']) * weight`
3. Test with CLI (`python fuzzy_ga_study_planner.py`)

### **Change GA Weights**
1. In `evaluate_fitness()`, update `alpha`, `beta`, `gamma` values
2. Rerun web app; experiment with test courses

### **Add PDF Section**
1. Find `export_pdf()` route in `app.py`
2. Append to `story` list using ReportLab Paragraph/Table objects
3. Example: `story.append(Paragraph(f'Text here', style))`

### **Change UI Colors**
1. Edit `static/style.css` root CSS variables or hex colors
2. Or edit `templates/index.html` inline styles
3. Reload browser (F5) due to cache-control headers

---

## Testing & Validation

**No automated test suite.** Manual testing workflow:
1. **CLI:** `python fuzzy_ga_study_planner.py` → Enter courses interactively
2. **Desktop:** `python fuzzy_ga_study_planner_gui.py` → GUI window
3. **Web:** `python app.py` → Open http://localhost:5000 → Add 2-3 courses, tweak parameters, generate

**Sanity checks:**
- Final fitness ≥ initial fitness (GA converges)
- All scheduled courses are unique (no duplicate IDs in schedule)
- Daily hours never exceed max_hours_per_day

---

## Performance Notes

- **GA runtime:** O(pop_size × generations × days × slots) ≈ 50 × 100 × 7 × 3 = 105k evaluations (~1-2 sec on modern CPU)
- **Bottleneck:** `evaluate_fitness()` called millions of times; nested loops with numpy calls
- **Optimization opportunity:** Vectorize fitness calculation (parallelize evaluations)
- **Frontend:** Canvas chart rendering can lag with 200+ fitness history points; consider downsampling

---

## Documentation Cross-References

- **Concept Explanations:** [UNDERSTANDING_CONCEPTS.md](../UNDERSTANDING_CONCEPTS.md)
- **User Guide:** [WEB_UI_GUIDE.md](../WEB_UI_GUIDE.md)
- **Quick Start:** [QUICK_START.md](../QUICK_START.md)
- **File Structure:** [FILES_GUIDE.md](../FILES_GUIDE.md)
