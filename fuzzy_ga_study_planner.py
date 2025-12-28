"""
Fuzzy-GA Based Personalized Study Schedule Generator
Author: University Student (ID: 201902007)
Course: CSE 316 - Artificial Intelligence Lab
Date: December 2025

Project Description:
This system generates a personalized weekly study schedule using:
- Genetic Algorithm (GA) for schedule optimization
- Fuzzy Logic for stress level modeling
"""

import numpy as np
import random
from datetime import datetime, timedelta
import json

# ============================================================================
# PART 1: FUZZY LOGIC SYSTEM FOR STRESS CALCULATION
# ============================================================================

class FuzzyStressCalculator:
    """
    Fuzzy logic system to calculate daily stress level.
    Inputs: DailyStudyHours, AverageCourseDifficulty
    Output: StressLevel (numeric 0-1)
    """
    
    def triangular_mf(self, x, a, b, c):
        """Triangular membership function with proper boundary handling"""
        # Handle edge case where a == b (left shoulder)
        if a == b:
            if x <= a:
                return 1.0
            elif x >= c:
                return 0.0
            else:
                return (c - x) / (c - b) if c != b else 0.0
        # Handle edge case where b == c (right shoulder)
        if b == c:
            if x >= c:
                return 1.0
            elif x <= a:
                return 0.0
            else:
                return (x - a) / (b - a) if b != a else 0.0
        # Normal triangular case
        if x < a or x > c:
            return 0.0
        elif x == b:
            return 1.0
        elif a <= x < b:
            return (x - a) / (b - a)
        else:  # b < x <= c
            return (c - x) / (c - b)
    
    def trapezoidal_mf(self, x, a, b, c, d):
        """Trapezoidal membership function with proper boundary handling"""
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
        """Convert hours to fuzzy membership values"""
        # Clamp hours to valid range [0, 8]
        hours = max(0, min(hours, 8))
        
        # Define membership functions for hours (0-6 range, extended to 8)
        # Low: peaks at 0, goes to 0 at 2
        if hours <= 0:
            low = 1.0
        elif hours < 2:
            low = 1.0 - (hours / 2.0)
        else:
            low = 0.0
            
        # Medium: rises from 1, peaks at 3, falls to 0 at 5
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
            
        # High: rises from 4, peaks at 6+
        if hours <= 4:
            high = 0.0
        elif hours < 6:
            high = (hours - 4) / 2.0
        else:
            high = 1.0
            
        return {'low': low, 'medium': medium, 'high': high}
    
    def fuzzify_difficulty(self, difficulty):
        """Convert difficulty to fuzzy membership values"""
        # Clamp difficulty to valid range [1, 5]
        difficulty = max(1, min(difficulty, 5))
        
        # Easy: peaks at 1, goes to 0 at 2.5
        if difficulty <= 1:
            easy = 1.0
        elif difficulty < 2.5:
            easy = (2.5 - difficulty) / 1.5
        else:
            easy = 0.0
            
        # Medium: rises from 2, peaks at 3, falls to 0 at 4
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
            
        # Hard: rises from 3.5, peaks at 5
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
        
        # Rule 1: low hours AND easy difficulty → low stress
        stress_mf['low'] += min(hours_mf['low'], difficulty_mf['easy']) * 0.8
        
        # Rule 2: medium hours AND medium difficulty → medium stress
        stress_mf['medium'] += min(hours_mf['medium'], difficulty_mf['medium']) * 0.7
        
        # Rule 3: high hours AND hard difficulty → high stress
        stress_mf['high'] += min(hours_mf['high'], difficulty_mf['hard']) * 0.9
        
        # Rule 4: high hours AND easy difficulty → low stress
        stress_mf['low'] += min(hours_mf['high'], difficulty_mf['easy']) * 0.6
        
        # Rule 5: medium hours AND hard difficulty → high stress
        stress_mf['high'] += min(hours_mf['medium'], difficulty_mf['hard']) * 0.9
        
        # Rule 6: low hours AND hard difficulty → HIGH stress (not enough time for hard course!)
        stress_mf['high'] += min(hours_mf['low'], difficulty_mf['hard']) * 0.95
        
        # Rule 7: low hours AND medium difficulty → medium stress
        stress_mf['medium'] += min(hours_mf['low'], difficulty_mf['medium']) * 0.7
        
        # Normalize
        total = sum(stress_mf.values())
        if total > 0:
            for key in stress_mf:
                stress_mf[key] /= total
        
        return stress_mf
    
    def defuzzify(self, stress_mf):
        """
        Defuzzification using Center of Gravity (CoG)
        Low stress = 0.2, Medium = 0.5, High = 0.8
        """
        stress_value = (stress_mf['low'] * 0.2 + 
                       stress_mf['medium'] * 0.5 + 
                       stress_mf['high'] * 0.8)
        return min(1.0, max(0.0, stress_value))
    
    def calculate_stress(self, daily_hours, avg_difficulty):
        """Main method: Calculate stress for a day"""
        hours_mf = self.fuzzify_hours(daily_hours)
        difficulty_mf = self.fuzzify_difficulty(avg_difficulty)
        stress_mf = self.apply_fuzzy_rules(hours_mf, difficulty_mf)
        stress_value = self.defuzzify(stress_mf)
        return stress_value


# ============================================================================
# PART 2: GENETIC ALGORITHM FOR SCHEDULE OPTIMIZATION
# ============================================================================

class StudyScheduleGA:
    """
    Genetic Algorithm for study schedule optimization.
    Chromosome: array of length (days * slots) with course IDs or 0 (rest).
    """
    
    def __init__(self, courses, days=7, slots_per_day=3, max_hours_per_day=4):
        """
        Initialize GA parameters.
        
        Args:
            courses: list of dicts with keys: 'id', 'name', 'difficulty', 'exam_days_away'
            days: number of days in schedule (default 7)
            slots_per_day: number of study slots per day (default 3, each ~1.5 hrs)
            max_hours_per_day: maximum study hours per day
        """
        self.courses = courses
        self.days = days
        self.slots_per_day = slots_per_day
        self.max_hours_per_day = max_hours_per_day
        self.chromosome_length = days * slots_per_day
        self.hours_per_slot = 1.5  # hours
        self.fuzzy_calculator = FuzzyStressCalculator()
        
    def create_random_chromosome(self):
        """Create a random valid schedule chromosome"""
        chromosome = []
        daily_slots = [0] * self.days  # Track slots used per day
        
        for day in range(self.days):
            for slot in range(self.slots_per_day):
                # Decide: course or rest (probability based on available hours)
                available_slots = int(self.max_hours_per_day / self.hours_per_slot)
                
                if daily_slots[day] < available_slots:
                    # Assign random course (or rest with 30% probability)
                    if random.random() < 0.7:
                        course_id = random.choice([c['id'] for c in self.courses] + [0])
                    else:
                        course_id = 0  # rest
                    
                    if course_id != 0:
                        daily_slots[day] += 1
                else:
                    course_id = 0  # rest (max hours reached)
                
                chromosome.append(course_id)
        
        return chromosome
    
    def create_initial_population(self, pop_size=50):
        """Create initial population"""
        return [self.create_random_chromosome() for _ in range(pop_size)]
    
    def evaluate_fitness(self, chromosome):
        """
        Calculate fitness score for a schedule.
        Fitness = α * coverage - β * overload_penalty - γ * stress_penalty
        """
        alpha = 5.0   # weight for coverage
        beta = 2.0    # weight for overload
        gamma = 3.0   # weight for stress
        
        # Coverage score: how many courses have study slots
        courses_covered = set(c for c in chromosome if c != 0)
        coverage_score = len(courses_covered)
        
        # Overload penalty: days exceeding max hours
        overload_penalty = 0
        stress_penalty = 0
        
        for day in range(self.days):
            day_start = day * self.slots_per_day
            day_end = day_start + self.slots_per_day
            day_slots = chromosome[day_start:day_end]
            day_hours = sum(1 for s in day_slots if s != 0) * self.hours_per_slot
            
            # Overload penalty
            if day_hours > self.max_hours_per_day:
                overload_penalty += (day_hours - self.max_hours_per_day) ** 2
            
            # Stress penalty from fuzzy logic
            avg_difficulty = 0
            non_zero_slots = [s for s in day_slots if s != 0]
            if non_zero_slots:
                avg_difficulty = np.mean([
                    next(c['difficulty'] for c in self.courses if c['id'] == s)
                    for s in non_zero_slots
                ])
            
            stress = self.fuzzy_calculator.calculate_stress(day_hours, avg_difficulty)
            stress_penalty += stress
        
        # Final fitness
        fitness = (alpha * coverage_score - 
                  beta * overload_penalty - 
                  gamma * stress_penalty)
        
        return max(0, fitness)  # Ensure non-negative
    
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
    
    def evolve(self, pop_size=50, generations=100):
        """Main GA evolution loop"""
        population = self.create_initial_population(pop_size)
        best_fitness_history = []
        
        for gen in range(generations):
            # Evaluate fitness
            fitness_scores = [self.evaluate_fitness(ind) for ind in population]
            best_fitness_history.append(max(fitness_scores))
            
            # Selection
            selected = self.selection(population, fitness_scores)
            
            # Crossover and mutation
            new_population = []
            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]
                child1, child2 = self.crossover(parent1, parent2)
                new_population.append(self.mutate(child1))
                new_population.append(self.mutate(child2))
            
            population = new_population[:pop_size]
            
            if (gen + 1) % 20 == 0:
                print(f"Generation {gen + 1}: Best Fitness = {best_fitness_history[-1]:.2f}")
        
        # Return best schedule
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
# PART 3: MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    print("=" * 70)
    print("FUZZY-GA BASED PERSONALIZED STUDY SCHEDULE GENERATOR")
    print("=" * 70)
    print()
    
    # Define sample courses
    courses = [
        {'id': 1, 'name': 'CSE 316 (AI Lab)', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 3xx (Database)', 'difficulty': 3, 'exam_days_away': 8},
        {'id': 3, 'name': 'CSE 3xx (Web Dev)', 'difficulty': 2, 'exam_days_away': 15},
        {'id': 4, 'name': 'CSE 3xx (Network)', 'difficulty': 4, 'exam_days_away': 12},
    ]
    
    print("Sample Courses:")
    for course in courses:
        print(f"  [{course['id']}] {course['name']} - Difficulty: {course['difficulty']}/5, Exam in {course['exam_days_away']} days")
    print()
    
    # Initialize GA
    print("Initializing Genetic Algorithm...")
    ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=4)
    
    # Run evolution
    print("Running GA evolution for 100 generations...")
    print()
    best_schedule, fitness_history = ga.evolve(pop_size=50, generations=100)
    
    print()
    print("=" * 70)
    print("OPTIMIZED STUDY SCHEDULE")
    print("=" * 70)
    print()
    
    readable_schedule = ga.schedule_to_readable(best_schedule)
    for day, slots in readable_schedule.items():
        print(f"\n{day}:")
        for slot, activity in slots.items():
            print(f"  {slot:15s}: {activity}")
    
    print()
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print(f"Initial Best Fitness:     {fitness_history[0]:.2f}")
    print(f"Final Best Fitness:       {fitness_history[-1]:.2f}")
    print(f"Fitness Improvement:      {(fitness_history[-1] - fitness_history[0]):.2f}")
    print()
    
    return best_schedule, ga, fitness_history


if __name__ == "__main__":
    best_schedule, ga, fitness_history = main()
