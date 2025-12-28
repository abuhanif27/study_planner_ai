"""
Comprehensive Test Suite for Fuzzy-GA Study Schedule Generator
"""

import sys
import json
import traceback

# Add current directory to path
sys.path.insert(0, '.')

from fuzzy_ga_study_planner_gui import FuzzyStressCalculator, StudyScheduleGA

def test_fuzzy_stress_calculator():
    """Test the Fuzzy Logic stress calculator"""
    print("=" * 60)
    print("TEST: FuzzyStressCalculator")
    print("=" * 60)
    
    fuzzy = FuzzyStressCalculator()
    errors = []
    
    # Test 1: Low hours, low difficulty -> low stress
    stress = fuzzy.calculate_stress(1, 1)
    print(f"  Low hours (1h), Easy difficulty (1): stress = {stress:.2f}")
    if stress > 0.5:
        errors.append(f"Expected low stress for 1h/easy, got {stress}")
    
    # Test 2: High hours, high difficulty -> high stress
    stress = fuzzy.calculate_stress(6, 5)
    print(f"  High hours (6h), Hard difficulty (5): stress = {stress:.2f}")
    if stress < 0.5:
        errors.append(f"Expected high stress for 6h/hard, got {stress}")
    
    # Test 3: Zero hours
    stress = fuzzy.calculate_stress(0, 3)
    print(f"  Zero hours (0h), Medium difficulty (3): stress = {stress:.2f}")
    if stress < 0 or stress > 1:
        errors.append(f"Stress out of bounds: {stress}")
    
    # Test 4: Edge case - negative hours (should handle gracefully)
    try:
        stress = fuzzy.calculate_stress(-1, 3)
        print(f"  Negative hours (-1h): stress = {stress:.2f}")
    except Exception as e:
        errors.append(f"Failed on negative hours: {e}")
    
    # Test 5: Edge case - difficulty out of range
    try:
        stress = fuzzy.calculate_stress(3, 10)
        print(f"  Difficulty out of range (10): stress = {stress:.2f}")
    except Exception as e:
        errors.append(f"Failed on high difficulty: {e}")
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_genetic_algorithm_basic():
    """Test basic GA functionality"""
    print("\n" + "=" * 60)
    print("TEST: StudyScheduleGA Basic Operations")
    print("=" * 60)
    
    courses = [
        {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8}
    ]
    
    errors = []
    
    # Test 1: Create GA instance
    try:
        ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=4)
        print(f"  GA Instance created: chromosome_length = {ga.chromosome_length}")
    except Exception as e:
        errors.append(f"Failed to create GA: {e}")
        print(f"  FAILED: {e}")
        return False
    
    # Test 2: Create random chromosome
    try:
        chromosome = ga.create_random_chromosome()
        print(f"  Random chromosome: length = {len(chromosome)}")
        if len(chromosome) != ga.chromosome_length:
            errors.append(f"Chromosome length mismatch: {len(chromosome)} != {ga.chromosome_length}")
    except Exception as e:
        errors.append(f"Failed to create chromosome: {e}")
    
    # Test 3: Create population
    try:
        pop = ga.create_initial_population(pop_size=10)
        print(f"  Population created: size = {len(pop)}")
        if len(pop) != 10:
            errors.append(f"Population size mismatch: {len(pop)} != 10")
    except Exception as e:
        errors.append(f"Failed to create population: {e}")
    
    # Test 4: Evaluate fitness
    try:
        fitness = ga.evaluate_fitness(chromosome)
        print(f"  Fitness evaluation: {fitness:.2f}")
        if fitness < 0:
            errors.append(f"Negative fitness: {fitness}")
    except Exception as e:
        errors.append(f"Failed to evaluate fitness: {e}")
    
    # Test 5: Validate chromosome
    try:
        valid = ga.is_valid_chromosome(chromosome)
        print(f"  Chromosome validity: {valid}")
    except Exception as e:
        errors.append(f"Failed to validate chromosome: {e}")
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_genetic_algorithm_evolution():
    """Test GA evolution"""
    print("\n" + "=" * 60)
    print("TEST: StudyScheduleGA Evolution")
    print("=" * 60)
    
    courses = [
        {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8},
        {'id': 3, 'name': 'CSE 407', 'difficulty': 5, 'exam_days_away': 5}
    ]
    
    errors = []
    
    try:
        ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=4)
        
        # Run evolution
        best_schedule, fitness_history = ga.evolve(pop_size=20, generations=10)
        
        print(f"  Evolution completed: {len(fitness_history)} generations")
        print(f"  Initial fitness: {fitness_history[0]:.2f}")
        print(f"  Final fitness: {fitness_history[-1]:.2f}")
        
        # Check fitness history
        if len(fitness_history) != 10:
            errors.append(f"Fitness history length: {len(fitness_history)} != 10")
        
        # Convert to readable
        readable = ga.schedule_to_readable(best_schedule)
        print(f"  Days in schedule: {len(readable)}")
        
        if len(readable) != 7:
            errors.append(f"Schedule days: {len(readable)} != 7")
        
    except Exception as e:
        errors.append(f"Evolution failed: {e}")
        traceback.print_exc()
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "=" * 60)
    print("TEST: Edge Cases")
    print("=" * 60)
    
    errors = []
    
    # Test 1: Single course
    print("  Testing single course...")
    try:
        courses = [{'id': 1, 'name': 'Only Course', 'difficulty': 3, 'exam_days_away': 7}]
        ga = StudyScheduleGA(courses, days=3, slots_per_day=2, max_hours_per_day=3)
        best, history = ga.evolve(pop_size=10, generations=5)
        print(f"    Single course: OK (fitness={history[-1]:.2f})")
    except Exception as e:
        errors.append(f"Single course failed: {e}")
        print(f"    Single course: FAILED - {e}")
    
    # Test 2: Many courses
    print("  Testing many courses (10)...")
    try:
        courses = [{'id': i, 'name': f'Course {i}', 'difficulty': (i % 5) + 1, 'exam_days_away': 10} 
                   for i in range(1, 11)]
        ga = StudyScheduleGA(courses, days=7, slots_per_day=4, max_hours_per_day=6)
        best, history = ga.evolve(pop_size=20, generations=10)
        print(f"    10 courses: OK (fitness={history[-1]:.2f})")
    except Exception as e:
        errors.append(f"Many courses failed: {e}")
        print(f"    10 courses: FAILED - {e}")
    
    # Test 3: Very small max hours
    print("  Testing small max hours (1.5)...")
    try:
        courses = [
            {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
            {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8}
        ]
        ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=1.5)
        best, history = ga.evolve(pop_size=10, generations=5)
        print(f"    Small max hours: OK (fitness={history[-1]:.2f})")
    except Exception as e:
        errors.append(f"Small max hours failed: {e}")
        print(f"    Small max hours: FAILED - {e}")
    
    # Test 4: Single day
    print("  Testing single day...")
    try:
        courses = [
            {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10}
        ]
        ga = StudyScheduleGA(courses, days=1, slots_per_day=3, max_hours_per_day=4)
        best, history = ga.evolve(pop_size=10, generations=5)
        print(f"    Single day: OK (fitness={history[-1]:.2f})")
    except Exception as e:
        errors.append(f"Single day failed: {e}")
        print(f"    Single day: FAILED - {e}")
    
    # Test 5: Max hours less than one slot
    print("  Testing max hours < slot duration (1.0)...")
    try:
        courses = [
            {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10}
        ]
        ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=1.0)
        best, history = ga.evolve(pop_size=10, generations=5)
        # This should result in all rest days since 1.0 < 1.5 (hours_per_slot)
        readable = ga.schedule_to_readable(best)
        print(f"    Max hours < slot: OK (fitness={history[-1]:.2f})")
    except Exception as e:
        errors.append(f"Max hours < slot failed: {e}")
        print(f"    Max hours < slot: FAILED - {e}")
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_schedule_to_readable():
    """Test schedule conversion to readable format"""
    print("\n" + "=" * 60)
    print("TEST: Schedule to Readable Conversion")
    print("=" * 60)
    
    courses = [
        {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8}
    ]
    
    errors = []
    
    try:
        ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=4)
        
        # Create a known chromosome
        # 21 slots (7 days * 3 slots), alternating courses and rest
        chromosome = [1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
        
        readable = ga.schedule_to_readable(chromosome)
        
        print(f"  Days in schedule: {list(readable.keys())}")
        
        # Check each day has the expected keys
        required_keys = {'Total Hours', 'Avg Difficulty', 'Stress Level'}
        for day, slots in readable.items():
            missing = required_keys - set(slots.keys())
            if missing:
                errors.append(f"Day {day} missing keys: {missing}")
        
        # Check first day structure
        monday = readable.get('Monday', {})
        print(f"  Monday slots: {[k for k in monday.keys() if k not in required_keys]}")
        print(f"  Monday Total Hours: {monday.get('Total Hours')}")
        print(f"  Monday Stress Level: {monday.get('Stress Level')}")
        
    except Exception as e:
        errors.append(f"Conversion failed: {e}")
        traceback.print_exc()
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_crossover_mutation():
    """Test crossover and mutation operators"""
    print("\n" + "=" * 60)
    print("TEST: Crossover and Mutation Operators")
    print("=" * 60)
    
    courses = [
        {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8}
    ]
    
    errors = []
    
    try:
        ga = StudyScheduleGA(courses, days=7, slots_per_day=3, max_hours_per_day=4)
        
        parent1 = ga.create_random_chromosome()
        parent2 = ga.create_random_chromosome()
        
        # Test crossover
        child1, child2 = ga.crossover(parent1, parent2, crossover_rate=1.0)
        print(f"  Crossover: parent1 len={len(parent1)}, child1 len={len(child1)}")
        
        if len(child1) != len(parent1):
            errors.append(f"Crossover changed length: {len(child1)} != {len(parent1)}")
        
        # Verify children are valid
        if not ga.is_valid_chromosome(child1):
            errors.append("Crossover produced invalid child1")
        if not ga.is_valid_chromosome(child2):
            errors.append("Crossover produced invalid child2")
        
        # Test mutation
        mutated = ga.mutate(parent1, mutation_rate=0.5)
        print(f"  Mutation: original len={len(parent1)}, mutated len={len(mutated)}")
        
        if len(mutated) != len(parent1):
            errors.append(f"Mutation changed length: {len(mutated)} != {len(parent1)}")
        
        # Verify mutated is valid
        if not ga.is_valid_chromosome(mutated):
            errors.append("Mutation produced invalid chromosome")
        
    except Exception as e:
        errors.append(f"Operators failed: {e}")
        traceback.print_exc()
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_days_beyond_week():
    """Test scheduling beyond 7 days"""
    print("\n" + "=" * 60)
    print("TEST: Scheduling Beyond 7 Days")
    print("=" * 60)
    
    courses = [
        {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8}
    ]
    
    errors = []
    
    try:
        # Test with 10 days (beyond the day_names list of 7)
        ga = StudyScheduleGA(courses, days=10, slots_per_day=3, max_hours_per_day=4)
        best, history = ga.evolve(pop_size=10, generations=5)
        readable = ga.schedule_to_readable(best)
        
        print(f"  Days scheduled: {len(readable)}")
        print(f"  Day names: {list(readable.keys())}")
        
        if len(readable) != 10:
            errors.append(f"Expected 10 days, got {len(readable)}")
        
        # Check if days beyond 7 are named properly
        day_keys = list(readable.keys())
        if len(day_keys) > 7:
            for i in range(7, len(day_keys)):
                if not day_keys[i].startswith('Day'):
                    errors.append(f"Day {i+1} should be 'Day X' format, got: {day_keys[i]}")
        
        print(f"    10-day schedule: OK")
        
    except Exception as e:
        errors.append(f"10-day schedule failed: {e}")
        traceback.print_exc()
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def test_slots_beyond_three():
    """Test more than 3 slots per day"""
    print("\n" + "=" * 60)
    print("TEST: More Than 3 Slots Per Day")
    print("=" * 60)
    
    courses = [
        {'id': 1, 'name': 'CSE 316', 'difficulty': 4, 'exam_days_away': 10},
        {'id': 2, 'name': 'CSE 406', 'difficulty': 3, 'exam_days_away': 8}
    ]
    
    errors = []
    
    try:
        # Test with 5 slots per day (beyond the slot_names list of 3)
        ga = StudyScheduleGA(courses, days=3, slots_per_day=5, max_hours_per_day=6)
        best, history = ga.evolve(pop_size=10, generations=5)
        readable = ga.schedule_to_readable(best)
        
        # Count slots per day
        for day, slots in readable.items():
            slot_count = len([k for k in slots.keys() if k not in {'Total Hours', 'Avg Difficulty', 'Stress Level'}])
            print(f"  {day}: {slot_count} slots")
            if slot_count != 5:
                errors.append(f"Expected 5 slots for {day}, got {slot_count}")
        
        print(f"    5 slots/day: OK")
        
    except Exception as e:
        errors.append(f"5 slots/day failed: {e}")
        traceback.print_exc()
    
    if errors:
        print(f"\n  FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    else:
        print("\n  PASSED")
    
    return len(errors) == 0


def run_all_tests():
    """Run all tests and summarize"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUITE FOR FUZZY-GA STUDY PLANNER")
    print("=" * 70)
    
    results = []
    
    results.append(("Fuzzy Stress Calculator", test_fuzzy_stress_calculator()))
    results.append(("GA Basic Operations", test_genetic_algorithm_basic()))
    results.append(("GA Evolution", test_genetic_algorithm_evolution()))
    results.append(("Edge Cases", test_edge_cases()))
    results.append(("Schedule Conversion", test_schedule_to_readable()))
    results.append(("Crossover & Mutation", test_crossover_mutation()))
    results.append(("Days Beyond Week", test_days_beyond_week()))
    results.append(("Slots Beyond Three", test_slots_beyond_three()))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed < total:
        print("\n  ⚠️  Some tests failed! Please review the errors above.")
        return False
    else:
        print("\n  ✅ All tests passed!")
        return True


if __name__ == "__main__":
    run_all_tests()
