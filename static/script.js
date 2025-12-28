// Global state
let courses = [];
let lastResults = null;
let timeSlots = [
    { id: 1, start: '9:00 AM', end: '10:30 AM' },
    { id: 2, start: '11:00 AM', end: '12:30 PM' },
    { id: 3, start: '2:00 PM', end: '3:30 PM' },
    { id: 4, start: '4:00 PM', end: '5:30 PM' },
    { id: 5, start: '7:00 PM', end: '8:30 PM' }
];

// Toggle process dropdown
function toggleProcessDropdown() {
    const processContent = document.getElementById('processContent');
    const dropdownIcon = document.getElementById('dropdownIcon');

    if (processContent.classList.contains('hidden')) {
        processContent.classList.remove('hidden');
        dropdownIcon.style.transform = 'rotate(180deg)';
    } else {
        processContent.classList.add('hidden');
        dropdownIcon.style.transform = 'rotate(0deg)';
    }
}

// Initialize time slots display
function initializeTimeSlots() {
    updateTimeSlotsDisplay();
}

// Update time slots display
function updateTimeSlotsDisplay() {
    const display = document.getElementById('timeSlotsDisplay');
    display.innerHTML = timeSlots.map((slot, idx) => `
        <div class="flex items-center justify-between text-xs p-2 bg-white dark:bg-slate-700 rounded border border-gray-300 dark:border-gray-600">
            <div class="flex items-center gap-2">
                <span class="font-bold text-blue-600 dark:text-blue-400">Slot ${slot.id}</span>
                <span class="text-gray-600 dark:text-gray-400">${slot.start} - ${slot.end}</span>
            </div>
            <span class="text-gray-500">1.5h</span>
        </div>
    `).join('');
}

// Toggle customization panel
function toggleTimeSlotCustomization() {
    const panel = document.getElementById('timeSlotPanel');
    const inputs = document.getElementById('timeSlotInputs');

    if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        // Populate inputs
        inputs.innerHTML = timeSlots.map((slot, idx) => `
            <div class="space-y-1">
                <label class="text-xs font-semibold text-gray-700 dark:text-gray-300">Slot ${slot.id}</label>
                <div class="flex gap-2">
                    <input 
                        type="time" 
                        value="${timeSlotToHHMM(slot.start)}"
                        id="start_${idx}"
                        class="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-50"
                    />
                    <input 
                        type="time" 
                        value="${timeSlotToHHMM(slot.end)}"
                        id="end_${idx}"
                        class="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-50"
                    />
                </div>
            </div>
        `).join('');
    } else {
        panel.classList.add('hidden');
    }
}

// Convert time format (12h to 24h)
function timeSlotToHHMM(time12) {
    const parts = time12.match(/(\d+):(\d+)\s(AM|PM)/);
    if (!parts) return '09:00';
    let hours = parseInt(parts[1]);
    const minutes = parts[2];
    const period = parts[3];

    if (period === 'PM' && hours !== 12) hours += 12;
    if (period === 'AM' && hours === 12) hours = 0;

    return `${String(hours).padStart(2, '0')}:${minutes}`;
}

// Convert time format (24h to 12h)
function HHMMToTimeSlot(time24) {
    const [hours, minutes] = time24.split(':');
    let h = parseInt(hours);
    const period = h >= 12 ? 'PM' : 'AM';
    if (h > 12) h -= 12;
    if (h === 0) h = 12;
    return `${h}:${minutes} ${period}`;
}

// Save time slots
function saveTimeSlots() {
    const inputs = document.getElementById('timeSlotInputs');
    timeSlots = [];

    let slotId = 1;
    for (let i = 0; i < 5; i++) {
        const startInput = document.getElementById(`start_${i}`);
        const endInput = document.getElementById(`end_${i}`);

        if (startInput && endInput) {
            timeSlots.push({
                id: slotId++,
                start: HHMMToTimeSlot(startInput.value),
                end: HHMMToTimeSlot(endInput.value)
            });
        }
    }

    updateTimeSlotsDisplay();
    document.getElementById('timeSlotPanel').classList.add('hidden');
    showToast('✅ Time slots updated!', 'success');
}

// Dark Mode Toggle
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    const themeIcon = document.getElementById('themeIcon');

    // Initialize time slots
    initializeTimeSlots();

    // Check localStorage or system preference
    const isDark = localStorage.getItem('darkMode') === 'true' ||
        (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches);

    // Apply initial theme
    if (isDark) {
        html.classList.add('dark');
        themeIcon.classList.add('fa-sun');
        themeIcon.classList.remove('fa-moon');
    } else {
        html.classList.remove('dark');
        themeIcon.classList.add('fa-moon');
        themeIcon.classList.remove('fa-sun');
    }

    // Dark mode toggle click handler
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            const isDarkMode = html.classList.toggle('dark');
            localStorage.setItem('darkMode', isDarkMode);

            if (isDarkMode) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        });
    }

    // Update parameter displays
    const popElement = document.getElementById('population');
    if (popElement) {
        popElement.addEventListener('input', (e) => {
            const popVal = document.getElementById('popValue');
            if (popVal) popVal.textContent = e.target.value;
        });
    }

    const genElement = document.getElementById('generations');
    if (genElement) {
        genElement.addEventListener('input', (e) => {
            const genVal = document.getElementById('genValue');
            if (genVal) genVal.textContent = e.target.value;
        });
    }

    const daysElement = document.getElementById('days');
    if (daysElement) {
        daysElement.addEventListener('input', (e) => {
            const daysVal = document.getElementById('daysValue');
            if (daysVal) daysVal.textContent = e.target.value;
        });
    }

    const slotsElement = document.getElementById('slots');
    if (slotsElement) {
        slotsElement.addEventListener('input', (e) => {
            const slotsVal = document.getElementById('slotsValue');
            if (slotsVal) slotsVal.textContent = e.target.value;
        });
    }

    const maxHoursElement = document.getElementById('maxHours');
    if (maxHoursElement) {
        maxHoursElement.addEventListener('input', (e) => {
            const hoursVal = document.getElementById('hoursValue');
            if (hoursVal) hoursVal.textContent = e.target.value + 'h';
        });
    }

    const diffElement = document.getElementById('difficulty');
    if (diffElement) {
        diffElement.addEventListener('input', (e) => {
            const emojis = ['🟢', '🟡', '🟠', '🔴', '⚫'];
            const diffDisplay = document.getElementById('diffDisplay');
            if (diffDisplay) diffDisplay.textContent = e.target.value + ' ' + emojis[e.target.value - 1];
        });
    }

    const examElement = document.getElementById('examDays');
    if (examElement) {
        examElement.addEventListener('input', (e) => {
            const examDisplay = document.getElementById('examDisplay');
            if (examDisplay) examDisplay.textContent = e.target.value + ' days';
        });
    }

    // Allow Enter key to add course
    const courseNameElement = document.getElementById('courseName');
    if (courseNameElement) {
        courseNameElement.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addCourse();
        });
    }
});

// Show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `p-4 rounded-lg text-sm font-medium shadow-lg animate-fade-in border ${type === 'success' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border-green-300 dark:border-green-700' :
        type === 'error' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border-red-300 dark:border-red-700' :
            'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border-yellow-300 dark:border-yellow-700'
        }`;

    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Add course
async function addCourse() {
    const name = document.getElementById('courseName').value.trim();
    const difficulty = parseInt(document.getElementById('difficulty').value);
    const examDays = parseInt(document.getElementById('examDays').value);


    if (!name) {
        showToast('❌ Course name is required', 'error');
        return;
    }

    if (courses.some(c => c.name.toLowerCase() === name.toLowerCase())) {
        showToast('⚠️ This course already exists', 'error');
        return;
    }

    try {
        const response = await fetch('/api/courses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                difficulty: difficulty,
                exam_days: examDays
            })
        });

        const data = await response.json();

        if (response.ok) {
            courses.push(data.course);
            renderCourses();
            document.getElementById('courseName').value = '';
            document.getElementById('difficulty').value = 3;
            document.getElementById('examDays').value = 7;
            document.getElementById('diffDisplay').textContent = '3 🟠';
            document.getElementById('examDisplay').textContent = '7 days';
            showToast(`✅ Course "${name}" added!`, 'success');
        } else {
            showToast(data.errors?.join(', ') || '❌ Error adding course', 'error');
        }
    } catch (error) {
        showToast('❌ Error: ' + error.message, 'error');
    }
}

// Render courses list
function renderCourses() {
    const coursesList = document.getElementById('coursesList');
    const courseCount = document.getElementById('courseCount');

    courseCount.textContent = courses.length;

    if (courses.length === 0) {
        coursesList.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 text-center py-8">No courses added yet</p>';
        return;
    }

    const emojis = ['🟢', '🟡', '🟠', '🔴', '⚫'];
    coursesList.innerHTML = courses.map((course, index) => `
        <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow animate-fade-in">
            <div>
                <p class="font-medium text-gray-900 dark:text-gray-50">${emojis[course.difficulty - 1]} ${course.name}</p>
                <div class="flex gap-2 mt-1">
                    <span class="text-xs bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">Diff: ${course.difficulty}</span>
                    <span class="text-xs bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 px-2 py-1 rounded">Exam: ${course.exam_days}d</span>
                </div>
            </div>
            <button onclick="removeCourse(${index})" class="text-red-500 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/20 p-2 rounded transition-colors">
                <i class="fas fa-trash text-sm"></i>
            </button>
        </div>
    `).join('');
}

// Remove course
function removeCourse(index) {
    const name = courses[index].name;
    courses.splice(index, 1);
    renderCourses();
    showToast(`🗑️ Course "${name}" removed`, 'warning');
}

// Clear all courses
function clearAllCourses() {
    if (courses.length === 0) {
        showToast('⚠️ No courses to clear', 'warning');
        return;
    }

    if (confirm(`Delete all ${courses.length} course(s)? This cannot be undone.`)) {
        courses = [];
        renderCourses();
        showToast('🗑️ All courses cleared', 'warning');
    }
}

// Generate schedule
async function generateSchedule() {
    if (courses.length === 0) {
        showToast('❌ Add at least one course first!', 'error');
        return;
    }

    const parameters = {
        population: parseInt(document.getElementById('population').value),
        generations: parseInt(document.getElementById('generations').value),
        days: parseInt(document.getElementById('days').value),
        slots: parseInt(document.getElementById('slots').value),
        max_hours: parseInt(document.getElementById('maxHours').value)
    };

    // Validate parameters
    const totalSlots = parameters.days * parameters.slots;
    const maxHoursAvailable = totalSlots * 1.5;
    const minHoursNeeded = courses.length * 1.5;

    if (maxHoursAvailable < minHoursNeeded) {
        showToast(`⚠️ Insufficient time: ${maxHoursAvailable.toFixed(1)}h available, ${minHoursNeeded.toFixed(1)}h needed!`, 'error');
        return;
    }

    // Disable button during generation
    const generateBtn = document.getElementById('generateBtn');
    const originalText = generateBtn.innerHTML;
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                courses: courses,
                parameters: parameters
            })
        });

        const data = await response.json();

        if (response.ok) {
            lastResults = data;
            displayResults(data);
            showToast('✅ Schedule generated successfully!', 'success');
        } else {
            showToast('❌ ' + (data.error || 'Error generating schedule'), 'error');
        }
    } catch (error) {
        showToast('❌ Error: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalText;
    }
}

// Display results with animated process visualization
function displayResults(data) {
    const stats = data.statistics;
    const params = data.parameters || {
        population: 50,
        generations: 50,
        days: 7,
        slots: 3,
        max_hours: 4
    };

    // Update stat cards
    document.getElementById('statFitness').textContent = stats.final_fitness.toFixed(2);
    document.getElementById('statCoverage').textContent = stats.coverage.toFixed(1) + '%';
    document.getElementById('statStress').textContent = stats.avg_stress.toFixed(2);
    document.getElementById('statOverload').textContent = stats.avg_overload.toFixed(2);

    // Show and animate process visualization
    showProcessVisualization(data, params);

    // Render schedule
    renderSchedule(data.schedule);

    // Show results section
    document.getElementById('resultsCard').classList.remove('hidden');
    document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Animated Process Visualization
function showProcessVisualization(data, params) {
    const processViz = document.getElementById('processViz');
    processViz.classList.remove('hidden');

    // Initialize step displays
    document.getElementById('initPopSize').textContent = params.population;
    document.getElementById('initCourses').textContent = courses.length;
    document.getElementById('initDays').textContent = params.days;
    document.getElementById('maxGen').textContent = params.generations;

    // Step 1: Initialization (immediate)
    setTimeout(() => {
        document.getElementById('step1').classList.remove('opacity-30');
        document.getElementById('step1').classList.add('opacity-100', 'border-l-4', 'border-green-500');
        document.getElementById('step1-count').innerHTML = '✓';
    }, 300);

    // Step 2: Fitness Calculation
    setTimeout(() => {
        document.getElementById('step2').classList.remove('opacity-30');
        document.getElementById('step2').classList.add('opacity-100', 'border-l-4', 'border-green-500');
        document.getElementById('initialFitness').textContent = data.statistics.initial_fitness.toFixed(2);
        document.getElementById('step2-count').innerHTML = '✓';
    }, 800);

    // Step 3: Evolution with progress animation
    setTimeout(() => {
        document.getElementById('step3').classList.remove('opacity-30');
        document.getElementById('step3').classList.add('opacity-100', 'border-l-4', 'border-green-500');

        // Animate generations
        const fitnessHistory = data.fitness_history || [];
        const totalGens = fitnessHistory.length;

        // Animate progression through generations
        let currentGen = 0;
        const genInterval = setInterval(() => {
            currentGen++;
            const progress = (currentGen / totalGens) * 100;

            document.getElementById('currentGen').textContent = currentGen;
            document.getElementById('bestFitnessGen').textContent = fitnessHistory[currentGen - 1]?.toFixed(2) || '-';
            document.getElementById('genPercent').textContent = Math.floor(progress);
            document.getElementById('genProgressBar').style.width = progress + '%';

            if (currentGen >= totalGens) {
                clearInterval(genInterval);
                document.getElementById('step3-count').innerHTML = '✓';

                // Step 4: Final Result
                setTimeout(() => {
                    document.getElementById('step4').classList.remove('opacity-30');
                    document.getElementById('step4').classList.add('opacity-100', 'border-l-4', 'border-green-500');
                    document.getElementById('finalFitnessViz').textContent = data.statistics.final_fitness.toFixed(2);
                    document.getElementById('improvementViz').innerHTML = `<span class="text-green-600 dark:text-green-400">+${(data.statistics.final_fitness - data.statistics.initial_fitness).toFixed(2)}</span>`;
                    document.getElementById('genRun').textContent = totalGens;
                    document.getElementById('step4-count').innerHTML = '✓';

                    // Draw fitness chart
                    drawFitnessChart(fitnessHistory);
                }, 500);
            }
        }, 20);
    }, 1300);
}

// Draw Fitness History Chart
function drawFitnessChart(fitnessHistory) {
    if (!fitnessHistory || fitnessHistory.length === 0) return;

    const canvas = document.getElementById('fitnessChart');
    if (!canvas) return;

    // Destroy existing chart if it exists
    if (window.fitnessChartInstance) {
        window.fitnessChartInstance.destroy();
    }

    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Calculate statistics
    const initial = fitnessHistory[0];
    const final = fitnessHistory[fitnessHistory.length - 1];
    const improvement = final - initial;
    const improvementPercent = (improvement / initial * 100).toFixed(1);

    // Update statistics display
    document.getElementById('chartInitial').textContent = initial.toFixed(2);
    document.getElementById('chartFinal').textContent = final.toFixed(2);
    document.getElementById('chartImprovement').textContent = `+${improvement.toFixed(2)} (+${improvementPercent}%)`;

    // Prepare data for Chart.js
    const labels = fitnessHistory.map((_, i) => `Gen ${i + 1}`);

    // Calculate a smoothed trend line (moving average)
    const smoothedData = [];
    const windowSize = Math.max(1, Math.floor(fitnessHistory.length / 20));

    for (let i = 0; i < fitnessHistory.length; i++) {
        const start = Math.max(0, i - Math.floor(windowSize / 2));
        const end = Math.min(fitnessHistory.length, i + Math.ceil(windowSize / 2));
        const sum = fitnessHistory.slice(start, end).reduce((a, b) => a + b, 0);
        smoothedData.push(sum / (end - start));
    }

    window.fitnessChartInstance = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Fitness',
                    data: fitnessHistory,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    borderWidth: 2,
                    pointRadius: 2,
                    pointBackgroundColor: '#a855f7',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1,
                    tension: 0.3,
                    fill: true,
                    pointHoverRadius: 5
                },
                {
                    label: 'Trend Line (Smoothed)',
                    data: smoothedData,
                    borderColor: '#06b6d4',
                    borderWidth: 3,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: false,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: isDark ? '#cbd5e1' : '#64748b',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12,
                            weight: '500'
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                filler: {
                    propagate: true
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                    titleColor: isDark ? '#f1f5f9' : '#1e293b',
                    bodyColor: isDark ? '#cbd5e1' : '#64748b',
                    borderColor: isDark ? '#475569' : '#e2e8f0',
                    borderWidth: 1,
                    padding: 12,
                    titleFont: {
                        family: "'Poppins', sans-serif",
                        size: 13,
                        weight: 'bold'
                    },
                    bodyFont: {
                        family: "'Poppins', sans-serif",
                        size: 12
                    },
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        color: isDark ? 'rgba(100, 116, 139, 0.1)' : 'rgba(229, 231, 235, 0.3)',
                        drawBorder: false
                    },
                    ticks: {
                        color: isDark ? '#94a3b8' : '#78716c',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 11
                        },
                        maxTicksLimit: 8,
                        callback: function (value) {
                            if (value % Math.floor(fitnessHistory.length / 5) === 0 || value === fitnessHistory.length - 1) {
                                return labels[value];
                            }
                            return '';
                        }
                    }
                },
                y: {
                    display: true,
                    beginAtZero: false,
                    grid: {
                        color: isDark ? 'rgba(100, 116, 139, 0.15)' : 'rgba(229, 231, 235, 0.5)',
                        drawBorder: false
                    },
                    ticks: {
                        color: isDark ? '#94a3b8' : '#78716c',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 11
                        },
                        callback: function (value) {
                            return value.toFixed(1);
                        },
                        padding: 10
                    },
                    title: {
                        display: true,
                        text: 'Fitness Score',
                        color: isDark ? '#cbd5e1' : '#64748b',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

// Get time period icon and label
function getTimePeriodIcon(timeSlotStart) {
    // Extract hour from time string (e.g., "9:00 AM" -> 9)
    const match = timeSlotStart.match(/(\d+):/);
    if (!match) return { icon: '😴', label: 'Rest Time', bgColor: 'bg-blue-50 dark:bg-blue-900/10', icon_class: 'fa-moon' };

    const hour = parseInt(match[1]);
    const isPM = timeSlotStart.includes('PM') && hour !== 12;
    const adjHour = isPM ? hour + 12 : (hour === 12 ? 0 : hour);

    // Morning: 6 AM - 12 PM
    if (adjHour >= 6 && adjHour < 12) {
        return { icon: '🌅', label: 'Morning Rest', bgColor: 'bg-yellow-50 dark:bg-yellow-900/10', icon_class: 'fa-sun' };
    }
    // Afternoon: 12 PM - 6 PM
    else if (adjHour >= 12 && adjHour < 18) {
        return { icon: '☀️', label: 'Afternoon Rest', bgColor: 'bg-orange-50 dark:bg-orange-900/10', icon_class: 'fa-sun' };
    }
    // Night: 6 PM - 6 AM
    else {
        return { icon: '🌙', label: 'Night Rest', bgColor: 'bg-indigo-50 dark:bg-indigo-900/10', icon_class: 'fa-moon' };
    }
}

// Render schedule
function renderSchedule(schedule) {
    const container = document.getElementById('scheduleContainer');
    const days = Object.entries(schedule);
    const totalDays = days.length;

    // Calculate column width based on number of days
    const colWidth = Math.max(160, Math.floor(100 / totalDays));

    let html = `
    <div class="w-full">
        <!-- Header -->
        <div class="text-center mb-8">
            <h2 class="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
                📅 Your Personalized Study Schedule
            </h2>
            <p class="text-gray-600 dark:text-gray-400">Optimized for maximum productivity and minimal stress • ${totalDays} days planned</p>
        </div>

        <!-- Schedule Table -->
        <div class="w-full overflow-x-auto rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-900">
            <table class="w-full border-collapse table-fixed" style="min-width: ${totalDays * 160}px;">
                <!-- Table Header -->
                <thead>
                    <tr class="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
    `;

    // Add day headers
    for (const [day, slots] of days) {
        const isStudyDay = Object.values(slots).some(s => s !== 'Rest' && typeof s === 'string' && !s.includes('Total') && !s.includes('Stress') && !s.includes('Difficulty'));
        const stress = slots['Stress Level'] || 'Low';
        let stressIcon = '🟢';
        let stressBadgeColor = 'bg-green-400/30';
        if (stress.includes('Medium')) { stressIcon = '🟡'; stressBadgeColor = 'bg-yellow-400/30'; }
        if (stress.includes('High')) { stressIcon = '🔴'; stressBadgeColor = 'bg-red-400/30'; }

        html += `
                        <th class="px-3 py-4 text-white font-bold text-center border-r border-white/10 last:border-r-0" style="width: ${100 / totalDays}%;">
                            <div class="flex flex-col items-center gap-1">
                                <span class="text-xl">${isStudyDay ? '📚' : '😴'}</span>
                                <span class="text-base font-semibold">${day}</span>
                                <span class="text-xs ${stressBadgeColor} px-2 py-0.5 rounded-full">${stressIcon} ${stress}</span>
                            </div>
                        </th>
        `;
    }

    html += `
                    </tr>
                </thead>
                <tbody>
    `;

    // Find max slots
    let maxSlots = 0;
    for (const [day, slots] of days) {
        let slotCount = 0;
        for (const [slot, activity] of Object.entries(slots)) {
            if (!slot.includes('Total') && !slot.includes('Difficulty') && !slot.includes('Stress')) {
                slotCount++;
            }
        }
        maxSlots = Math.max(maxSlots, slotCount);
    }

    // Generate rows for each time slot
    for (let i = 0; i < maxSlots; i++) {
        const timeSlot = timeSlots[i] || { start: '-', end: '-' };
        const timePeriod = getTimePeriodIcon(timeSlot.start);

        html += `
                    <tr class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50/50 dark:hover:bg-slate-800/30 transition-colors">
        `;

        for (const [day, slots] of days) {
            const slotEntries = Object.entries(slots).filter(([k, v]) => !k.includes('Total') && !k.includes('Difficulty') && !k.includes('Stress'));
            const [slotKey, activity] = slotEntries[i] || ['', null];

            if (activity === 'Rest') {
                html += `
                        <td class="px-2 py-3 text-center border-r border-gray-100 dark:border-gray-800 last:border-r-0">
                            <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800/50 dark:to-gray-700/50 rounded-lg p-3 mx-auto">
                                <div class="text-lg mb-1">${timePeriod.icon}</div>
                                <p class="font-medium text-gray-500 dark:text-gray-400 text-xs">${timePeriod.label}</p>
                                <p class="text-xs text-gray-400 dark:text-gray-500">${timeSlot.start} - ${timeSlot.end}</p>
                                <span class="inline-block mt-1.5 text-xs bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded-full">Rest</span>
                            </div>
                        </td>
                `;
            } else if (activity) {
                html += `
                        <td class="px-2 py-3 text-center border-r border-gray-100 dark:border-gray-800 last:border-r-0">
                            <div class="bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/20 rounded-lg p-3 mx-auto border border-blue-200 dark:border-blue-700/50 hover:shadow-md transition-shadow">
                                <div class="text-lg mb-1">📖</div>
                                <p class="font-bold text-blue-900 dark:text-blue-200 text-xs truncate" title="${activity}">${activity}</p>
                                <p class="text-xs text-blue-600 dark:text-blue-400">${timeSlot.start} - ${timeSlot.end}</p>
                                <span class="inline-block mt-1.5 text-xs bg-blue-500 text-white px-2 py-0.5 rounded-full font-medium">1.5h</span>
                            </div>
                        </td>
                `;
            } else {
                html += `
                        <td class="px-2 py-3 text-center border-r border-gray-100 dark:border-gray-800 last:border-r-0">
                            <div class="text-gray-300 dark:text-gray-700 py-6">—</div>
                        </td>
                `;
            }
        }

        html += `
                    </tr>
        `;
    }

    // Stats row
    html += `
                    <tr class="bg-gradient-to-r from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 border-t-2 border-gray-300 dark:border-gray-600">
    `;

    for (const [day, slots] of days) {
        const totalHours = slots['Total Hours'] || '0.0';
        const difficulty = slots['Avg Difficulty'] || '0.0';
        const load = (parseFloat(difficulty) * parseFloat(totalHours)).toFixed(1);
        const intensityPercent = Math.min((load / 20) * 100, 100);
        const intensityColor = intensityPercent < 25 ? 'bg-green-500' : intensityPercent < 50 ? 'bg-blue-500' : intensityPercent < 75 ? 'bg-amber-500' : 'bg-red-500';

        html += `
                        <td class="px-2 py-4 border-r border-gray-200 dark:border-gray-700 last:border-r-0">
                            <div class="space-y-2">
                                <div class="flex justify-center gap-3 text-center">
                                    <div>
                                        <p class="text-xs text-gray-500 dark:text-gray-400">⏱️</p>
                                        <p class="text-lg font-bold text-gray-900 dark:text-white">${totalHours}h</p>
                                    </div>
                                    <div>
                                        <p class="text-xs text-gray-500 dark:text-gray-400">🎯</p>
                                        <p class="text-lg font-bold text-gray-900 dark:text-white">${difficulty}</p>
                                    </div>
                                </div>
                                <div class="w-full h-1.5 bg-gray-300 dark:bg-gray-700 rounded-full overflow-hidden">
                                    <div class="h-full ${intensityColor} transition-all duration-500" style="width: ${intensityPercent}%"></div>
                                </div>
                            </div>
                        </td>
        `;
    }

    html += `
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Legend -->
        <div class="mt-6 flex flex-wrap justify-center gap-6 text-sm">
            <div class="flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-green-500"></span>
                <span class="text-gray-600 dark:text-gray-400">🟢 Low Stress</span>
            </div>
            <div class="flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-yellow-500"></span>
                <span class="text-gray-600 dark:text-gray-400">🟡 Medium Stress</span>
            </div>
            <div class="flex items-center gap-2">
                <span class="w-4 h-4 rounded-full bg-red-500"></span>
                <span class="text-gray-600 dark:text-gray-400">🔴 High Stress</span>
            </div>
            <div class="flex items-center gap-2">
                <span class="w-4 h-4 rounded bg-blue-500"></span>
                <span class="text-gray-600 dark:text-gray-400">📖 Study Session</span>
            </div>
            <div class="flex items-center gap-2">
                <span class="w-4 h-4 rounded bg-gray-400"></span>
                <span class="text-gray-600 dark:text-gray-400">😴 Rest Period</span>
            </div>
        </div>
    </div>
    `;

    container.innerHTML = html;
}

// Export results
function exportResults() {
    if (!lastResults) {
        showToast('❌ No results to export', 'error');
        return;
    }

    const data = {
        timestamp: new Date().toISOString(),
        courses: courses,
        parameters: lastResults.parameters,
        statistics: lastResults.statistics,
        schedule: lastResults.schedule
    };

    // Show loading toast
    showToast('📄 Generating PDF...', 'success');

    // Send to backend to generate PDF
    fetch('/api/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `study_schedule_${new Date().toISOString().split('T')[0]}.pdf`;
            link.click();
            URL.revokeObjectURL(url);
            showToast('✅ PDF exported successfully!', 'success');
        })
        .catch(error => {
            showToast('❌ Error generating PDF: ' + error.message, 'error');
        });
}