import random
import time
import threading
import logging
import json
from graphviz import Digraph

logging.basicConfig(level=logging.INFO)

class AI:
    def __init__(self, name, role, capabilities):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.tasks = []
        self.is_busy = False
        self.performance_record = []

    def collaborate(self, other_ai, task):
        logging.info(f"{self.name} collaborating with {other_ai.name} on task: {task.description}")
        other_ai.tasks.append(task)

    def record_performance(self, task, time_taken):
        self.performance_record.append((task.description, time_taken))
        # This data could be analyzed later to improve task handling

class Task:
    def __init__(self, id, description, priority, deadline, dependencies=None):
        self.id = id
        self.description = description
        self.priority = priority
        self.deadline = deadline
        self.dependencies = dependencies if dependencies else []
        self.status = "Pending"
        self.assigned_to = None
        self.is_completed = False

    def is_ready_to_execute(self):
        return all(dep.is_completed for dep in self.dependencies)

class TaskManager:
    def __init__(self):
        self.tasks = []

    def dynamic_prioritization(self):
        for task in self.tasks:
            if task.status == "Pending" and task.deadline:
                days_to_deadline = (time.strptime(task.deadline, "%Y-%m-%d") - time.localtime()).tm_yday
                if days_to_deadline <= 2:
                    task.priority = 1
                elif days_to_deadline <= 5:
                    task.priority = 2

    def assign_task(self, task):
        suitable_ais = [ai for ai in ais if task.description.lower() in ai.capabilities and not ai.is_busy]
        if suitable_ais and task.is_ready_to_execute():
            chosen_ai = random.choice(suitable_ais)
            chosen_ai.tasks.append(task)
            task.assigned_to = chosen_ai.name
            task.status = "Assigned"
            logging.info(f"Task '{task.description}' assigned to {chosen_ai.name}.")
        elif not task.is_ready_to_execute():
            logging.info(f"Task '{task.description}' is waiting for dependencies.")
        else:
            logging.warning(f"No suitable AI found for task: {task.description}")

    def update_task_status(self, task_id, new_status):
        for task in self.tasks:
            if task.id == task_id:
                task.status = new_status
                break

    def handle_errors(self, task, error_message):
        logging.error(f"Error in task {task.id} ({task.description}): {error_message}")
        task.status = "Error"

    def save_state(self, filename="task_manager_state.json"):
        with open(filename, 'w') as file:
            json.dump([task.__dict__ for task in self.tasks], file)
        logging.info("Task manager state saved.")

    def load_state(self, filename="task_manager_state.json"):
        try:
            with open(filename, 'r') as file:
                tasks = json.load(file)
                for task_data in tasks:
                    task = Task(**task_data)
                    self.tasks.append(task)
            logging.info("Task manager state loaded.")
        except FileNotFoundError:
            logging.warning("No saved state found. Starting fresh.")

    def visualize_task_dependencies(self):
        dot = Digraph()
        for task in self.tasks:
            dot.node(str(task.id), task.description)
            for dep in task.dependencies:
                dot.edge(str(dep.id), str(task.id))
        dot.render('task_dependencies', view=True)
        logging.info("Task dependencies visualized.")

class AIThread(threading.Thread):
    def __init__(self, ai):
        super().__init__()
        self.ai = ai

    def run(self):
        while True:
            if self.ai.tasks:
                task = self.ai.tasks.pop(0)
                self.ai.is_busy = True
                start_time = time.time()
                try:
                    logging.info(f"{self.ai.name} is working on: {task.description}")
                    time.sleep(random.randint(1, 5))  # Simulate task execution
                    if random.choice([True, False]):  # Randomly simulate an error
                        raise Exception("Simulated execution error")
                    task.is_completed = True
                    task.status = "Completed"
                    logging.info(f"{self.ai.name} has completed: {task.description}")
                except Exception as e:
                    task_manager.handle_errors(task, str(e))
                finally:
                    self.ai.is_busy = False
                    end_time = time.time()
                    self.ai.record_performance(task, end_time - start_time)
            else:
                time.sleep(1)  # Idle state

# Create AI agents
ais = [
    AI("Jexi", "Data Analyst", ["analyze data", "predictive analysis", "data cleaning", "generate reports"]),
    AI("Nova", "Task Executor", ["cross-platform execution", "automation", "trigger-based automation", "automated testing"]),
    AI("Astra", "Research & Customer Support", ["market research", "customer support", "content curation", "trend analysis"]),
    AI("Sung", "Project Coordinator", ["task management", "code execution", "code review", "documentation"])
]

# Load previous state or create new tasks
task_manager = TaskManager()
task_manager.load_state()

# If no tasks loaded, create new tasks with dependencies
if not task_manager.tasks:
    task1 = Task(1, "Analyze various datasets", 1, "2024-09-01")
    task2 = Task(2, "Execute system backup", 1, "2024-08-31")
    task3 = Task(3, "Conduct market research on competitors", 2, "2024-09-15", dependencies=[task1])
    task4 = Task(4, "Review and optimize code for security", 2, "2024-09-10", dependencies=[task2])
    task_manager.tasks = [task1, task2, task3, task4]

# Create threads for AIs
ai_threads = [AIThread(ai) for ai in ais]

# Start AI threads
for thread in ai_threads:
    thread.start()

# Main loop for dynamic task management
try:
    while True:
        task_manager.dynamic_prioritization()

        for task in task_manager.tasks:
            if task.status == "Pending":
                task_manager.assign_task(task)
            elif task.status == "Assigned" and task.is_completed:
                task_manager.update_task_status(task.id, "Completed")

        task_manager.visualize_task_dependencies()
        task_manager.save_state()

        time.sleep(5)  # Update every 5 seconds
except KeyboardInterrupt:
    logging.info("Shutting down...")
    task_manager.save_state()
