"""
Fuzzy-GA Based Personalized Study Schedule Generator - Interactive Tkinter GUI
Author: University Student (ID: 201902007)
Course: CSE 316 - Artificial Intelligence Lab
Date: December 2025

This is an interactive GUI version of the study planner using Tkinter.
Enhanced with modern UI/UX and comprehensive validation.
"""

import numpy as np
import random
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime, timedelta
import threading


COLORS = {
    'primary': '#2196F3',      
    'success': '#4CAF50',      
    'warning': '#FF9800',      
    'danger': '#F44336',       
    'info': '#00BCD4',         
    'light_bg': '#F5F5F5',     
    'dark_bg': '#FAFAFA',      
    'text': '#212121',         
    'light_text': '#666666'    
}


class FuzzyStressCalculator:
    """Fuzzy logic system to calculate daily stress level."""
    
    def triangular_mf(self, x, a, b, c):
        """Triangular membership function with proper boundary handling"""
        
        if a == b:
            if x <= a:
                return 1.0
            elif x >= c:
                return 0.0
            else:
                return (c - x) / (c - b) if c != b else 0.0
        
        if b == c:
            if x >= c:
                return 1.0
            elif x <= a:
                return 0.0
            else:
                return (x - a) / (b - a) if b != a else 0.0
        
        if x < a or x > c:
            return 0.0
        elif x == b:
            return 1.0
        elif a <= x < b:
            return (x - a) / (b - a)
        else:  
            return (c - x) / (c - b)
    
    def trapezoidal_mf(self, x, a, b, c, d):

        if x < a or x > d:
            return 0.0
        elif a <= x <= b:
            if a == b:
                return 1.0
            return (x - a) / (b - a)
        elif b < x < c:
            return 1.0
        elif c <= x <= d:
            if c == d:
                return 1.0
            return (d - x) / (d - c)
        return 0.0
    
    def fuzzify_hours(self, hours):
        hours = max(0, min(hours, 8))
        if hours <= 0:
            low = 1.0
        elif hours < 2:
            low = 1.0 - (hours / 2.0)
        else:
            low = 0.0
            
        if hours <= 1:
            medium = 0.0
        elif hours < 3:
            medium = (hours - 1) / 2.0
        elif hours <= 3:
            medium = 1.0
        elif hours < 5:
            medium = (5 - hours) / 2.0
        else:
            medium = 0.0
            
    
        if hours <= 4:
            high = 0.0
        elif hours < 6:
            high = (hours - 4) / 2.0
        else:
            high = 1.0
            
        return {'low': low, 'medium': medium, 'high': high}
    
    def fuzzify_difficulty(self, difficulty):
        difficulty = max(1, min(difficulty, 5))
        
        if difficulty <= 1:
            easy = 1.0
        elif difficulty < 2.5:
            easy = (2.5 - difficulty) / 1.5
        else:
            easy = 0.0
            
        if difficulty <= 2:
            medium = 0.0
        elif difficulty < 3:
            medium = (difficulty - 2) / 1.0
        elif difficulty <= 3:
            medium = 1.0
        elif difficulty < 4:
            medium = (4 - difficulty) / 1.0
        else:
            medium = 0.0
            

        if difficulty <= 3.5:
            hard = 0.0
        elif difficulty < 5:
            hard = (difficulty - 3.5) / 1.5
        else:
            hard = 1.0
            
        return {'easy': easy, 'medium': medium, 'hard': hard}
    
    def apply_fuzzy_rules(self, hours_mf, difficulty_mf):
        """
        Fuzzy rule base:
        Rule 1: IF hours=low AND difficulty=easy THEN stress=low
        Rule 2: IF hours=medium AND difficulty=medium THEN stress=medium
        Rule 3: IF hours=high AND difficulty=hard THEN stress=high
        Rule 4: IF hours=high AND difficulty=easy THEN stress=low
        Rule 5: IF hours=medium AND difficulty=hard THEN stress=high
        Rule 6: IF hours=low AND difficulty=hard THEN stress=high (TIME PRESSURE)
        Rule 7: IF hours=low AND difficulty=medium THEN stress=medium
        """
        stress_mf = {'low': 0, 'medium': 0, 'high': 0}
        
        # Rule 1: low hours AND easy difficulty -> low stress
        stress_mf['low'] += min(hours_mf['low'], difficulty_mf['easy']) * 0.8
        
        # Rule 2: medium hours AND medium difficulty -> medium stress
        stress_mf['medium'] += min(hours_mf['medium'], difficulty_mf['medium']) * 0.7
        
        # Rule 3: high hours AND hard difficulty -> high stress
        stress_mf['high'] += min(hours_mf['high'], difficulty_mf['hard']) * 0.9
        
        # Rule 4: high hours AND easy difficulty -> low stress
        stress_mf['low'] += min(hours_mf['high'], difficulty_mf['easy']) * 0.6
        
        # Rule 5: medium hours AND hard difficulty -> high stress
        stress_mf['high'] += min(hours_mf['medium'], difficulty_mf['hard']) * 0.9
        
        # Rule 6: low hours AND hard difficulty -> HIGH stress (not enough time for hard course!)
        stress_mf['high'] += min(hours_mf['low'], difficulty_mf['hard']) * 0.95
        
        # Rule 7: low hours AND medium difficulty -> medium stress
        stress_mf['medium'] += min(hours_mf['low'], difficulty_mf['medium']) * 0.7
        
        total = sum(stress_mf.values())
        if total > 0:
            for key in stress_mf:
                stress_mf[key] /= total
        
        return stress_mf
    
    def defuzzify(self, stress_mf):
        """Defuzzification using Center of Gravity (CoG)"""
        stress_value = (stress_mf['low'] * 0.2 + 
                       stress_mf['medium'] * 0.5 + 
                       stress_mf['high'] * 0.8)
        return min(1.0, max(0.0, stress_value))
    
    def calculate_stress(self, daily_hours, avg_difficulty):
        hours_mf = self.fuzzify_hours(daily_hours)
        difficulty_mf = self.fuzzify_difficulty(avg_difficulty)
        stress_mf = self.apply_fuzzy_rules(hours_mf, difficulty_mf)
        stress_value = self.defuzzify(stress_mf)
        return stress_value


class StudyScheduleGA:
    
    def __init__(self, courses, days=7, slots_per_day=3, max_hours_per_day=4):
        self.courses = courses
        self.days = days
        self.slots_per_day = slots_per_day
        self.max_hours_per_day = max_hours_per_day
        self.chromosome_length = days * slots_per_day
        self.hours_per_slot = 1.5
        self.fuzzy_calculator = FuzzyStressCalculator()
        
    def create_random_chromosome(self):
        """Create a random valid schedule chromosome"""
        chromosome = []
        daily_slots = [0] * self.days
        
        for day in range(self.days):
            for slot in range(self.slots_per_day):
                available_slots = int(self.max_hours_per_day / self.hours_per_slot)
                
                if daily_slots[day] < available_slots:
                    if random.random() < 0.7:
                        course_id = random.choice([c['id'] for c in self.courses] + [0])
                    else:
                        course_id = 0
                    
                    if course_id != 0:
                        daily_slots[day] += 1
                else:
                    course_id = 0
                
                chromosome.append(course_id)
        
        return chromosome
    
    def create_initial_population(self, pop_size=50):
        """Create initial population"""
        return [self.create_random_chromosome() for _ in range(pop_size)]
    
    def evaluate_fitness(self, chromosome):
        """Calculate fitness score for a schedule."""
        alpha = 5.0
        beta = 2.0
        gamma = 3.0
        
        courses_covered = set(c for c in chromosome if c != 0)
        coverage_score = len(courses_covered)
        
        overload_penalty = 0
        stress_penalty = 0
        
        for day in range(self.days):
            day_start = day * self.slots_per_day
            day_end = day_start + self.slots_per_day
            day_slots = chromosome[day_start:day_end]
            day_hours = sum(1 for s in day_slots if s != 0) * self.hours_per_slot
            
            if day_hours > self.max_hours_per_day:
                overload_penalty += (day_hours - self.max_hours_per_day) ** 2
            
            avg_difficulty = 0
            non_zero_slots = [s for s in day_slots if s != 0]
            if non_zero_slots:
                avg_difficulty = np.mean([
                    next(c['difficulty'] for c in self.courses if c['id'] == s)
                    for s in non_zero_slots
                ])
            
            stress = self.fuzzy_calculator.calculate_stress(day_hours, avg_difficulty)
            stress_penalty += stress
        
        fitness = (alpha * coverage_score - 
                  beta * overload_penalty - 
                  gamma * stress_penalty)
        
        return max(0, fitness)
    
    def selection(self, population, fitness_scores, tournament_size=3):
        """Tournament selection"""
        selected = []
        for _ in range(len(population)):
            idx = random.sample(range(len(population)), tournament_size)
            winner = max(idx, key=lambda i: fitness_scores[i])
            selected.append(population[winner].copy())
        return selected
    
    def is_valid_chromosome(self, chromosome):
        """Check if chromosome respects all constraints"""
        for day in range(self.days):
            day_start = day * self.slots_per_day
            day_end = day_start + self.slots_per_day
            day_slots = chromosome[day_start:day_end]
            day_hours = sum(1 for s in day_slots if s != 0) * self.hours_per_slot
            
            if day_hours > self.max_hours_per_day:
                return False
        return True
    
    def fix_chromosome(self, chromosome):
        """Fix chromosome to respect max_hours_per_day constraint"""
        fixed = chromosome.copy()
        for day in range(self.days):
            day_start = day * self.slots_per_day
            day_end = day_start + self.slots_per_day
            day_slots = fixed[day_start:day_end]
            
            # Count non-zero slots
            non_zero_count = sum(1 for s in day_slots if s != 0)
            max_slots = int(self.max_hours_per_day / self.hours_per_slot)
            
            # If exceeds limit, randomly convert excess slots to rest (0)
            if non_zero_count > max_slots:
                slots_to_remove = non_zero_count - max_slots
                non_zero_indices = [i for i in range(len(day_slots)) if day_slots[i] != 0]
                indices_to_clear = random.sample(non_zero_indices, slots_to_remove)
                
                for idx in indices_to_clear:
                    fixed[day_start + idx] = 0
        
        return fixed
    
    def crossover(self, parent1, parent2, crossover_rate=0.8):
        """One-point crossover with constraint validation"""
        if random.random() < crossover_rate:
            point = random.randint(1, len(parent1) - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            
            # Ensure children respect constraints
            if not self.is_valid_chromosome(child1):
                child1 = self.fix_chromosome(child1)
            if not self.is_valid_chromosome(child2):
                child2 = self.fix_chromosome(child2)
            
            return child1, child2
        return parent1.copy(), parent2.copy()
    
    def mutate(self, chromosome, mutation_rate=0.1):
        """Mutation: randomly change gene while respecting constraints"""
        mutated = chromosome.copy()
        for i in range(len(mutated)):
            if random.random() < mutation_rate:
                day = i // self.slots_per_day
                day_start = day * self.slots_per_day
                day_end = day_start + self.slots_per_day
                day_slots = mutated[day_start:day_end]
                
                # Count current non-zero slots in this day
                non_zero_count = sum(1 for s in day_slots if s != 0)
                max_slots = int(self.max_hours_per_day / self.hours_per_slot)
                
                # Only allow mutation if it won't exceed max hours
                if mutated[i] != 0:  # Currently has a course
                    # Can change to anything (including rest)
                    mutated[i] = random.choice([c['id'] for c in self.courses] + [0])
                else:  # Currently is rest
                    # Can only add course if it won't exceed limit
                    if non_zero_count < max_slots:
                        mutated[i] = random.choice([c['id'] for c in self.courses] + [0])
        
        # Final validation
        if not self.is_valid_chromosome(mutated):
            mutated = self.fix_chromosome(mutated)
        
        return mutated
    
    def evolve(self, pop_size=50, generations=100, progress_callback=None):
        """Main GA evolution loop with progress callback"""
        population = self.create_initial_population(pop_size)
        best_fitness_history = []
        
        for gen in range(generations):
            fitness_scores = [self.evaluate_fitness(ind) for ind in population]
            best_fitness_history.append(max(fitness_scores))
            
            selected = self.selection(population, fitness_scores)
            
            new_population = []
            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                child1, child2 = self.crossover(parent1, parent2)
                new_population.append(self.mutate(child1))
                new_population.append(self.mutate(child2))
            
            population = new_population[:pop_size]
            
            if progress_callback:
                progress_callback(gen + 1, generations, best_fitness_history[-1])
        
        final_fitness = [self.evaluate_fitness(ind) for ind in population]
        best_idx = np.argmax(final_fitness)
        best_schedule = population[best_idx]
        
        return best_schedule, best_fitness_history
    
    def schedule_to_readable(self, chromosome):
        """Convert chromosome to readable schedule"""
        schedule = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        slot_names = ['Morning', 'Afternoon', 'Evening']
        
        for day in range(self.days):
            day_name = day_names[day] if day < len(day_names) else f"Day {day}"
            schedule[day_name] = {}
            
            day_start = day * self.slots_per_day
            day_end = day_start + self.slots_per_day
            day_slots = chromosome[day_start:day_end]
            
            total_hours = 0
            difficulty_values = []
            
            for slot_idx, course_id in enumerate(day_slots):
                slot_name = slot_names[slot_idx] if slot_idx < len(slot_names) else f"Slot {slot_idx}"
                if course_id != 0:
                    course = next(c for c in self.courses if c['id'] == course_id)
                    schedule[day_name][slot_name] = course['name']
                    total_hours += self.hours_per_slot
                    difficulty_values.append(course['difficulty'])
                else:
                    schedule[day_name][slot_name] = 'Rest'
            
            avg_difficulty = np.mean(difficulty_values) if difficulty_values else 0
            stress = self.fuzzy_calculator.calculate_stress(total_hours, avg_difficulty)
            schedule[day_name]['Total Hours'] = f"{total_hours:.1f}"
            schedule[day_name]['Avg Difficulty'] = f"{avg_difficulty:.1f}"
            schedule[day_name]['Stress Level'] = f"{stress:.2f} ({self.stress_label(stress)})"
        
        return schedule
    
    @staticmethod
    def stress_label(stress_value):
        """Convert stress numeric value to label"""
        if stress_value < 0.33:
            return "Low"
        elif stress_value < 0.67:
            return "Medium"
        else:
            return "High"


# ============================================================================
# PART 3: TKINTER GUI APPLICATION
# ============================================================================

class StudyPlannerGUI:
    """Main GUI Application class with enhanced UI/UX"""
    
    def __init__(self, root):
        self.root = root
        self.root.title('🎓 Fuzzy-GA Study Schedule Generator - Interactive GUI')
        self.root.geometry('1200x950')
        self.root.minsize(1000, 800)
        
        # Configure style
        self.setup_styles()
        
        self.courses = []
        self.best_schedule = None
        self.fitness_history = None
        self.ga = None
        self.is_generating = False
        
        self.create_widgets()
    
    def setup_styles(self):
        """Configure modern styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground=COLORS['primary'])
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'), foreground=COLORS['text'])
        style.configure('Info.TLabel', font=('Arial', 9), foreground=COLORS['light_text'])
        style.configure('Success.TButton', font=('Arial', 10, 'bold'))
        style.configure('Danger.TButton', font=('Arial', 10, 'bold'))
        
        # Frame styling
        style.configure('Card.TFrame', relief='flat', borderwidth=2)
        style.configure('Header.TFrame', relief='flat')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Course Management
        course_frame = ttk.Frame(notebook)
        notebook.add(course_frame, text='Courses & Parameters')
        self.create_course_tab(course_frame)
        
        # Tab 2: Results
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text='Schedule Results')
        self.create_results_tab(results_frame)
    
    def create_course_tab(self, parent):
        """Create course management tab with modern UI"""
        # Configure grid
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Left panel - Course input
        left_frame = ttk.LabelFrame(parent, text='📚 Add Courses', padding=15)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)
        left_frame.columnconfigure(0, weight=1)
        
        # Course Name with label and info
        ttk.Label(left_frame, text='Course Name:', style='Header.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 2))
        ttk.Label(left_frame, text='(Max 50 characters)', style='Info.TLabel').grid(row=0, column=0, sticky='e', pady=(0, 2))
        self.course_name_entry = ttk.Entry(left_frame, width=40, font=('Arial', 10))
        self.course_name_entry.grid(row=1, column=0, sticky='ew', pady=(0, 12))
        self.course_name_entry.bind('<Return>', lambda e: self.add_course())
        
        # Difficulty with visual feedback
        ttk.Label(left_frame, text='Difficulty Level (1=Easy, 5=Hard):', style='Header.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 2))
        self.course_diff_var = tk.IntVar(value=3)
        self.course_diff_scale = ttk.Scale(left_frame, from_=1, to=5, orient=tk.HORIZONTAL, 
                                          variable=self.course_diff_var, command=self.update_difficulty_display)
        self.course_diff_scale.grid(row=3, column=0, sticky='ew', pady=(0, 5))
        self.course_diff_label = ttk.Label(left_frame, text='3 🟠', style='Header.TLabel', font=('Arial', 11, 'bold'))
        self.course_diff_label.grid(row=3, column=0, sticky='e', pady=(0, 5))
        
        # Exam Days
        ttk.Label(left_frame, text='Days Until Exam:', style='Header.TLabel').grid(row=4, column=0, sticky='w', pady=(10, 2))
        ttk.Label(left_frame, text='(1-365 days)', style='Info.TLabel').grid(row=4, column=0, sticky='e', pady=(10, 2))
        self.course_days_entry = ttk.Entry(left_frame, width=40, font=('Arial', 10))
        self.course_days_entry.insert(0, '7')
        self.course_days_entry.grid(row=5, column=0, sticky='ew', pady=(0, 12))
        
        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=6, column=0, sticky='ew', pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text='➕ Add Course', command=self.add_course).grid(row=0, column=0, sticky='ew', padx=(0, 5))
        ttk.Button(button_frame, text='🗑️ Clear All', command=self.clear_courses).grid(row=0, column=1, sticky='ew', padx=(5, 0))
        
        # Courses list
        ttk.Label(left_frame, text='Added Courses:', style='Header.TLabel').grid(row=7, column=0, sticky='w', pady=(15, 5))
        self.courses_listbox = tk.Listbox(left_frame, height=12, font=('Courier', 9), 
                                         bg='#FAFAFA', selectmode=tk.SINGLE, relief=tk.FLAT, bd=1)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.courses_listbox.yview)
        self.courses_listbox.config(yscrollcommand=scrollbar.set)
        self.courses_listbox.grid(row=8, column=0, sticky='nsew', pady=(0, 0))
        scrollbar.grid(row=8, column=1, sticky='ns')
        left_frame.rowconfigure(8, weight=1)
        
        # Right panel - GA parameters
        right_frame = ttk.LabelFrame(parent, text='⚙️ GA Parameters & Settings', padding=15)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=8, pady=8)
        right_frame.columnconfigure(0, weight=1)
        
        # Population Size
        self._create_parameter_slider(right_frame, 0, 'Population Size', 
                                     'Schedules to evaluate per generation', 10, 200, 50, 
                                     'self.pop_size_var', 'self.pop_size_label')
        
        # Generations
        self._create_parameter_slider(right_frame, 1, 'Generations', 
                                     'Evolution iterations (more = better)', 10, 200, 100,
                                     'self.gen_var', 'self.gen_label')
        
        # Days to Schedule
        self._create_parameter_slider(right_frame, 2, 'Days to Schedule', 
                                     'Planning horizon (3-7 days recommended)', 3, 7, 7,
                                     'self.days_var', 'self.days_label')
        
        # Slots per Day
        self._create_parameter_slider(right_frame, 3, 'Slots per Day', 
                                     'Study periods per day (~1.5h each)', 1, 5, 3,
                                     'self.slots_var', 'self.slots_label')
        
        # Max Hours per Day
        self._create_parameter_slider(right_frame, 4, 'Max Hours per Day', 
                                     '⚠️ Set high enough to accommodate courses!', 1, 8, 4,
                                     'self.max_hours_var', 'self.max_hours_label')
        
        # Generate button
        ttk.Button(right_frame, text='🚀 Generate Schedule', command=self.generate_schedule).grid(row=5, column=0, sticky='ew', pady=(20, 0), ipady=8)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(right_frame, variable=self.progress_var, maximum=100, mode='determinate').grid(row=6, column=0, sticky='ew', pady=(10, 0))
        self.progress_label = ttk.Label(right_frame, text='⏳ Ready to generate', style='Info.TLabel')
        self.progress_label.grid(row=7, column=0, sticky='w', pady=(5, 0))
    
    def _create_parameter_slider(self, parent, row, label, tooltip, from_val, to_val, default, var_name, label_var_name):
        """Helper to create parameter sliders with labels"""
        ttk.Label(parent, text=f'{label}:', style='Header.TLabel').grid(row=row*2, column=0, sticky='w', pady=(15, 2))
        ttk.Label(parent, text=tooltip, style='Info.TLabel').grid(row=row*2, column=0, sticky='e', pady=(15, 2))
        
        var = tk.IntVar(value=default)
        setattr(self, var_name.split('.')[-1], var)
        
        scale = ttk.Scale(parent, from_=from_val, to=to_val, orient=tk.HORIZONTAL, variable=var,
                         command=lambda v, vn=label_var_name: self._update_param_label(v, vn))
        scale.grid(row=row*2+1, column=0, sticky='ew', pady=(0, 10))
        
        label_widget = ttk.Label(parent, text=str(default), style='Header.TLabel', font=('Arial', 10, 'bold'))
        label_widget.grid(row=row*2+1, column=0, sticky='e', pady=(0, 10))
        setattr(self, label_var_name.split('.')[-1], label_widget)
    
    def update_difficulty_display(self, val):
        """Update difficulty display with emoji"""
        val_int = int(float(val))
        emojis = ['🟢', '🟡', '🟠', '🔴', '⚫']
        self.course_diff_label.config(text=f'{val_int} {emojis[val_int-1]}')
    
    def _update_param_label(self, val, label_var_name):
        """Update parameter label"""
        label_widget = getattr(self, label_var_name.split('.')[-1])
        label_widget.config(text=str(int(float(val))))
    
    def create_results_tab(self, parent):
        """Create results display tab with modern design"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        # Top panel - Controls with better styling
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=0, column=0, sticky='ew', padx=8, pady=8)
        control_frame.columnconfigure(0, weight=1)
        
        ttk.Label(control_frame, text='📊 Schedule Results', style='Title.TLabel').pack(side=tk.LEFT, padx=5)
        
        button_container = ttk.Frame(control_frame)
        button_container.pack(side=tk.RIGHT)
        ttk.Button(button_container, text='💾 Export Results', command=self.export_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text='🔄 Refresh', command=self.refresh_results).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky='ew')
        
        # Main results area with frame
        results_frame = ttk.Frame(parent)
        results_frame.grid(row=2, column=0, sticky='nsew', padx=8, pady=8)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=35, width=140, 
                                                      font=('Courier New', 9), 
                                                      state=tk.DISABLED, relief=tk.FLAT, bd=1,
                                                      bg='#FAFAFA')
        self.results_text.grid(row=0, column=0, sticky='nsew')
        
        # Status bar
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky='ew', padx=8, pady=5)
        ttk.Label(status_frame, text='ℹ️ Results will appear here after generation', style='Info.TLabel').pack(anchor='w')
    
    def update_difficulty_label(self, val):
        self.course_diff_label.config(text=str(int(float(val))))
    
    def update_pop_label(self, val):
        self.pop_size_label.config(text=str(int(float(val))))
    
    def update_gen_label(self, val):
        self.gen_label.config(text=str(int(float(val))))
    
    def update_days_label(self, val):
        self.days_label.config(text=str(int(float(val))))
    
    def update_slots_label(self, val):
        self.slots_label.config(text=str(int(float(val))))
    
    def update_max_hours_label(self, val):
        self.max_hours_label.config(text=str(int(float(val))))
    
    
    def validate_course_name(self, name):
        """Validate course name with detailed error messages"""
        if not name or len(name.strip()) == 0:
            return False, "❌ Course name cannot be empty"
        
        if len(name) > 50:
            return False, "❌ Course name is too long (max 50 characters)"
        
        if any(char in name for char in ['@', '#', '$', '%']):
            return False, "❌ Course name contains invalid characters"
        
        # Check for duplicates
        existing_names = [c['name'].lower() for c in self.courses]
        if name.lower() in existing_names:
            return False, f"❌ Course '{name}' already exists!"
        
        return True, "✓ Valid course name"
    
    def validate_exam_days(self, days_str):
        """Validate exam days with detailed error messages"""
        try:
            days = int(days_str)
        except ValueError:
            return False, "❌ Exam days must be a whole number"
        
        if days < 1:
            return False, "❌ Exam days must be at least 1"
        
        if days > 365:
            return False, "❌ Exam days cannot exceed 365"
        
        return True, f"✓ Valid ({days} days)"
    
    def validate_difficulty(self, difficulty):
        """Validate difficulty level"""
        if difficulty < 1 or difficulty > 5:
            return False, "❌ Difficulty must be between 1-5"
        return True, f"✓ Difficulty {difficulty}"
    
    def validate_parameters(self):
        """Validate all GA parameters"""
        errors = []
        
        days = self.days_var.get()
        slots = self.slots_var.get()
        max_hours = self.max_hours_var.get()
        
        if days < 3:
            errors.append("• Days to schedule: Minimum 3 days required")
        
        if slots < 1:
            errors.append("• Slots per day: Minimum 1 slot required")
        
        if max_hours < 1:
            errors.append("• Max hours per day: Minimum 1 hour required")
        
        # Calculate minimum hours needed
        if self.courses:
            avg_difficulty = np.mean([c['difficulty'] for c in self.courses])
            # Rough estimate: need at least 1 hour per course
            min_total_hours = len(self.courses) * 1.5
            available_hours = days * slots * 1.5
            
            if available_hours < min_total_hours:
                errors.append(
                    f"• Insufficient study time: You have {available_hours:.1f}h available "
                    f"but need ~{min_total_hours:.1f}h for {len(self.courses)} course(s)"
                )
        
        return errors
    
    def add_course(self):
        """Add a new course with comprehensive validation"""
        name = self.course_name_entry.get().strip()
        
        # Validate course name
        is_valid, message = self.validate_course_name(name)
        if not is_valid:
            messagebox.showerror('❌ Invalid Course Name', message)
            self.course_name_entry.focus()
            return
        
        # Validate exam days
        days_str = self.course_days_entry.get().strip()
        is_valid, message = self.validate_exam_days(days_str)
        if not is_valid:
            messagebox.showerror('❌ Invalid Exam Days', message)
            self.course_days_entry.focus()
            return
        
        days = int(days_str)
        
        # Validate difficulty
        difficulty = self.course_diff_var.get()
        is_valid, message = self.validate_difficulty(difficulty)
        if not is_valid:
            messagebox.showerror('❌ Invalid Difficulty', message)
            return
        
        # Add course
        new_course_id = len(self.courses) + 1
        new_course = {
            'id': new_course_id,
            'name': name,
            'difficulty': difficulty,
            'exam_days_away': days
        }
        self.courses.append(new_course)
        
        # Display in listbox with color coding
        difficulty_emoji = ['🟢', '🟡', '🟠', '🔴', '⚫'][difficulty - 1]
        display_text = f"{difficulty_emoji} {name:30s} | Diff: {difficulty}/5 | Exam: {days}d"
        self.courses_listbox.insert(tk.END, display_text)
        
        # Reset inputs
        self.course_name_entry.delete(0, tk.END)
        self.course_diff_var.set(3)
        self.course_days_entry.delete(0, tk.END)
        self.course_days_entry.insert(0, '7')
        self.course_name_entry.focus()
        
        # Show success message
        messagebox.showinfo('✓ Success', f'Course "{name}" added successfully!\nTotal courses: {len(self.courses)}')

    
    def clear_courses(self):
        """Clear all courses"""
        if self.courses:
            if messagebox.askyesno('⚠️ Confirm', f'Delete all {len(self.courses)} course(s)?\n\nThis action cannot be undone.'):
                self.courses.clear()
                self.courses_listbox.delete(0, tk.END)
                messagebox.showinfo('✓ Done', 'All courses cleared!')
    
    def generate_schedule(self):
        """Generate schedule with validation"""
        # Validate courses
        if not self.courses:
            messagebox.showerror('❌ No Courses', 'Please add at least one course before generating!')
            return
        
        # Validate parameters
        param_errors = self.validate_parameters()
        if param_errors:
            error_msg = "⚠️ Parameter Issues Found:\n\n" + "\n".join(param_errors) + \
                        "\n\n💡 Tip: Try increasing days or slots to have more study time"
            messagebox.showwarning('⚠️ Parameter Validation', error_msg)
            return
        
        if self.is_generating:
            messagebox.showwarning('⚠️ In Progress', 'Schedule generation is already running!')
            return
        
        self.is_generating = True
        self.progress_label.config(text='🔄 Initializing genetic algorithm...')
        
        thread = threading.Thread(target=self._run_ga)
        thread.daemon = True
        thread.start()
    
    def _run_ga(self):
        """Run GA in background thread"""
        try:
            pop_size = self.pop_size_var.get()
            generations = self.gen_var.get()
            days = self.days_var.get()
            slots = self.slots_var.get()
            max_hours = self.max_hours_var.get()
            
            # Initialize GA
            self.ga = StudyScheduleGA(self.courses, days=days, slots_per_day=slots, max_hours_per_day=max_hours)
            
            def progress_callback(gen, total, best_fitness):
                progress_value = (gen / total) * 100
                self.progress_var.set(progress_value)
                status = f'⚙️ Generation {gen}/{total} | Best Fitness: {best_fitness:.2f}'
                self.progress_label.config(text=status)
                self.root.update_idletasks()
            
            # Run evolution
            self.best_schedule, self.fitness_history = self.ga.evolve(
                pop_size=pop_size,
                generations=generations,
                progress_callback=progress_callback
            )
            
            # Display results
            self.refresh_results()
            self.progress_label.config(text='✅ Schedule generation completed successfully!')
            messagebox.showinfo('✅ Success', 
                f'🎯 Schedule Generated!\n\n'
                f'Initial Fitness: {self.fitness_history[0]:.2f}\n'
                f'Final Fitness: {self.fitness_history[-1]:.2f}\n'
                f'Improvement: {(self.fitness_history[-1] - self.fitness_history[0]):.2f}',
                icon=messagebox.INFO)
        
        except Exception as e:
            messagebox.showerror('❌ Error', f'Error during schedule generation:\n{str(e)}')
            self.progress_label.config(text='❌ Error during generation')
        
        finally:
            self.is_generating = False
    
    def refresh_results(self):
        """Refresh and display results with beautiful formatting"""
        if self.best_schedule is None or self.ga is None:
            messagebox.showwarning('⚠️ No Results', 'No schedule available. Generate one first!')
            return
        
        readable_schedule = self.ga.schedule_to_readable(self.best_schedule)
        
        # Build beautiful output
        output_text = ""
        output_text += "╔" + "═" * 98 + "╗\n"
        output_text += "║" + " " * 25 + "📚 OPTIMIZED STUDY SCHEDULE 📚" + " " * 43 + "║\n"
        output_text += "╚" + "═" * 98 + "╝\n\n"
        
        # Schedule details
        for day, slots_info in readable_schedule.items():
            # Color code days
            output_text += f"\n{'─' * 100}\n"
            output_text += f"📅 {day.upper()}\n"
            output_text += f"{'─' * 100}\n"
            
            for slot, activity in slots_info.items():
                if slot == 'Total Hours':
                    output_text += f"  ⏱️  {slot:25s}: {activity:20s} hours\n"
                elif slot == 'Avg Difficulty':
                    output_text += f"  📊 {slot:25s}: {activity:20s} / 5\n"
                elif slot == 'Stress Level':
                    stress_val = activity.split(' ')[0]
                    stress_label = activity.split('(')[1].rstrip(')')
                    icon = '🟢' if 'Low' in stress_label else '🟡' if 'Medium' in stress_label else '🔴'
                    output_text += f"  {icon} {slot:25s}: {activity}\n"
                elif activity != 'Rest':
                    output_text += f"  📖 {slot:25s}: {activity}\n"
                else:
                    output_text += f"  😴 {slot:25s}: {activity}\n"
        
        # Summary statistics with emojis
        output_text += "\n" + "╔" + "═" * 98 + "╗\n"
        output_text += "║" + " " * 30 + "📊 SUMMARY STATISTICS 📊" + " " * 43 + "║\n"
        output_text += "╚" + "═" * 98 + "╝\n\n"
        
        improvement = self.fitness_history[-1] - self.fitness_history[0]
        improvement_pct = (improvement / self.fitness_history[0] * 100) if self.fitness_history[0] > 0 else 0
        
        output_text += f"  🎯 Initial Best Fitness     : {self.fitness_history[0]:>8.2f}\n"
        output_text += f"  🏆 Final Best Fitness       : {self.fitness_history[-1]:>8.2f}\n"
        output_text += f"  📈 Fitness Improvement      : {improvement:>8.2f} ({improvement_pct:>6.1f}%)\n"
        output_text += f"  🔄 Number of Generations    : {len(self.fitness_history):>8d}\n"
        output_text += f"  📚 Total Courses            : {len(self.courses):>8d}\n"
        output_text += f"  ⏰ Total Study Days         : {self.ga.days:>8d}\n"
        output_text += f"  ⏳ Slots per Day            : {self.ga.slots_per_day:>8d}\n"
        output_text += f"  ⚙️  Max Hours per Day        : {self.ga.max_hours_per_day:>8d}h\n"
        
        # Course summary
        output_text += f"\n{'─' * 100}\n"
        output_text += "📋 COURSES INCLUDED:\n"
        output_text += f"{'─' * 100}\n"
        for i, course in enumerate(self.courses, 1):
            diff_emoji = ['🟢', '🟡', '🟠', '🔴', '⚫'][course['difficulty'] - 1]
            output_text += f"  {i}. {diff_emoji} {course['name']:40s} | Difficulty: {course['difficulty']}/5 | Exam: {course['exam_days_away']}d\n"
        
        output_text += f"\n{'═' * 100}\n"
        output_text += "✨ Schedule generated successfully! You can export these results for future reference.\n"
        output_text += f"{'═' * 100}\n"
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, output_text)
        self.results_text.config(state=tk.DISABLED)
    
    def export_results(self):
        """Export results to JSON file with validation"""
        if self.best_schedule is None:
            messagebox.showerror('❌ No Results', 'No results to export.\n\nGenerate a schedule first!')
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON Files', '*.json'), ('Text Files', '*.txt'), ('All Files', '*.*')],
            initialfile=f"study_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if filename:
            try:
                readable_schedule = self.ga.schedule_to_readable(self.best_schedule)
                export_data = {
                    'metadata': {
                        'timestamp': datetime.now().isoformat(),
                        'generated_by': 'Fuzzy-GA Study Planner v1.0'
                    },
                    'courses': self.courses,
                    'schedule': readable_schedule,
                    'statistics': {
                        'initial_fitness': float(self.fitness_history[0]),
                        'final_fitness': float(self.fitness_history[-1]),
                        'improvement': float(self.fitness_history[-1] - self.fitness_history[0]),
                        'total_generations': len(self.fitness_history),
                        'total_courses': len(self.courses),
                        'days_scheduled': self.ga.days
                    },
                    'fitness_history': self.fitness_history.tolist() if isinstance(self.fitness_history, np.ndarray) else self.fitness_history,
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                messagebox.showinfo('✅ Export Successful', 
                    f'Results exported successfully!\n\n'
                    f'📁 File: {filename}\n'
                    f'📊 Courses: {len(self.courses)}\n'
                    f'🎯 Final Fitness: {self.fitness_history[-1]:.2f}')
            
            except Exception as e:
                messagebox.showerror('❌ Export Error', f'Error exporting results:\n{str(e)}')


if __name__ == "__main__":
    root = tk.Tk()
    app = StudyPlannerGUI(root)
    root.mainloop()
