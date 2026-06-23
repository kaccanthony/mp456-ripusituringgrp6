import os
import sys
from datetime import date, datetime
from collections import deque

class Project:
    """Represents a single active project."""

    VALID_STATUSES = {"Pending", "In Progress", "Completed"}

    def __init__(self, id_number: int, title: str, size: int,
                priority: int, due_date: date, progress: int = 0,
                status: str = "Pending"):
        self.id_number = id_number
        self.title = title
        self.size = size
        self.priority = priority
        self.due_date = due_date
        self.progress = progress
        self.status = status

    # For saving to a file
    def to_file_line(self) -> str:
        return (f"{self.id_number}|{self.title}|{self.size}|"
                f"{self.priority}|{self.due_date}|{self.progress}|{self.status}")

    @classmethod
    def from_file_line(cls, line: str) -> "Project":
        parts = line.strip().split("|")
        if len(parts) != 7:
            raise ValueError(f"Malformed project line: {line!r}")
        id_number = int(parts[0])
        title = parts[1]
        size = int(parts[2])
        priority = int(parts[3])
        due_date = datetime.strptime(parts[4], "%Y-%m-%d").date()
        progress = int(parts[5])
        status = parts[6]
        return cls(id_number, title, size, priority, due_date, progress, status)

    def __repr__(self) -> str:
        return (f"Project(id={self.id_number}, title={self.title!r}, "
                f"priority={self.priority}, due={self.due_date})")

class CompletedProject:
    """Represents a project that has been finished."""

    def __init__(self, id_number: int, title: str, size: int,
                priority: int, due_date: date, completion_date: date):
        self.id_number = id_number
        self.title = title
        self.size = size
        self.priority = priority
        self.due_date = due_date
        self.completion_date = completion_date

    def to_file_line(self) -> str:
        return (f"{self.id_number}|{self.title}|{self.size}|"
                f"{self.priority}|{self.due_date}|{self.completion_date}")

    @classmethod
    def from_file_line(cls, line: str) -> "CompletedProject":
        parts = line.strip().split("|")
        if len(parts) != 6:
            raise ValueError(f"Malformed completed-project line: {line!r}")
        id_number = int(parts[0])
        title = parts[1]
        size = int(parts[2])
        priority = int(parts[3])
        due_date = datetime.strptime(parts[4], "%Y-%m-%d").date()
        completion_date = datetime.strptime(parts[5], "%Y-%m-%d").date()
        return cls(id_number, title, size, priority, due_date, completion_date)

#  FILE MANAGER

class FileManager:
    """Handles all file I/O for the three persistence files."""

    PROJECTS_FILE = "projects.txt"
    COMPLETED_FILE = "completed_projects.txt"
    SCHEDULE_FILE = "schedule.txt"

    @staticmethod
    def load_projects() -> dict[int, Project]:
        projects: dict[int, Project] = {}
        if not os.path.exists(FileManager.PROJECTS_FILE):
            return projects
        with open(FileManager.PROJECTS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    p = Project.from_file_line(line)
                    projects[p.id_number] = p
                except (ValueError, IndexError) as exc:
                    print(f"  [Warning] Skipping invalid project record: {exc}")
        return projects

    @staticmethod
    def save_projects(projects: dict[int, Project]) -> None:
        with open(FileManager.PROJECTS_FILE, "w") as f:
            for p in projects.values():
                f.write(p.to_file_line() + "\n")

    #  Completed Projects 
    @staticmethod
    def load_completed() -> list[CompletedProject]:
        completed: list[CompletedProject] = []
        if not os.path.exists(FileManager.COMPLETED_FILE):
            return completed
        with open(FileManager.COMPLETED_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    completed.append(CompletedProject.from_file_line(line))
                except (ValueError, IndexError) as exc:
                    print(f"  [Warning] Skipping invalid completed record: {exc}")
        return completed

    @staticmethod
    def save_completed(completed: list[CompletedProject]) -> None:
        with open(FileManager.COMPLETED_FILE, "w") as f:
            for cp in completed:
                f.write(cp.to_file_line() + "\n")

    #  Schedule 
    @staticmethod
    def load_schedule() -> deque[int]:
        queue: deque[int] = deque()
        if not os.path.exists(FileManager.SCHEDULE_FILE):
            return queue
        with open(FileManager.SCHEDULE_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split("|")
                    queue.append(int(parts[1]))
                except (ValueError, IndexError) as exc:
                    print(f"  [Warning] Skipping invalid schedule record: {exc}")
        return queue

    @staticmethod
    def save_schedule(queue: deque[int]) -> None:
        with open(FileManager.SCHEDULE_FILE, "w") as f:
            for pos, pid in enumerate(queue, start=1):
                f.write(f"{pos}|{pid}\n")



#  VALIDATORS


class ValidationError(Exception):
    pass


def validate_positive_int(value: str, field_name: str) -> int:
    """Parse and validate that a value is a positive integer."""
    try:
        n = int(value)
    except ValueError:
        raise ValidationError(f"{field_name} must be a whole number.")
    if n <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")
    return n


def validate_non_negative_int(value: str, field_name: str, max_val: int = None) -> int:
    try:
        n = int(value)
    except ValueError:
        raise ValidationError(f"{field_name} must be a whole number.")
    if n < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    if max_val is not None and n > max_val:
        raise ValidationError(f"{field_name} cannot exceed {max_val}.")
    return n


def validate_date(value: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidationError("Due date must be in YYYY-MM-DD format (e.g. 2026-07-10).")


def validate_title(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValidationError("Title cannot be empty.")
    return value

#  SCHEDULER

class Scheduler:
    """
    Builds a priority queue from active projects.
    Sort key: (priority ASC, due_date ASC, size ASC)
    """

    @staticmethod
    def build_queue(projects: dict[int, Project]) -> deque[int]:
        active = [p for p in projects.values() if p.status != "Completed"]
        sorted_projects = sorted(
            active,
            key=lambda p: (p.priority, p.due_date, p.size)
        )
        return deque(p.id_number for p in sorted_projects)

#  UI HELPERS

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def separator(char: str = "", width: int = 55) -> None:
    print(char * width)


def header(title: str, width: int = 55) -> None:
    separator("═", width)
    print(f"  {title}")
    separator("═", width)

def pause() -> None:
    input("\n  Press Enter to continue...")


def confirm(prompt: str = "Proceed? (Y/N): ") -> bool:
    while True:
        ans = input(f"\n  {prompt}").strip().upper()
        if ans in ("Y", "N"):
            return ans == "Y"
        print("  Please enter Y or N.")


def prompt(label: str) -> str:
    return input(f"  {label}: ").strip()

def display_project(p: Project) -> None:
    print(f"  ID       : {p.id_number}")
    print(f"  Title    : {p.title}")
    print(f"  Size     : {p.size} pages")
    print(f"  Priority : {p.priority}")
    print(f"  Due Date : {p.due_date}")
    print(f"  Progress : {p.progress}%")
    print(f"  Status   : {p.status}")

#  APPLICATION

class App:
    """Main application controller."""

    def __init__(self):
        self.projects: dict[int, Project] = FileManager.load_projects()
        self.completed: list[CompletedProject] = FileManager.load_completed()
        self.queue: deque[int] = FileManager.load_schedule()
        # Remove stale IDs from queue
        self._clean_queue()

    #  Internal helpers 

    def _clean_queue(self) -> None:
        self.queue = deque(
            pid for pid in self.queue
            if pid in self.projects and self.projects[pid].status != "Completed"
        )

    def _save_all(self) -> None:
        FileManager.save_projects(self.projects)
        FileManager.save_schedule(self.queue)

    def _rebuild_and_save_schedule(self) -> None:
        self.queue = Scheduler.build_queue(self.projects)
        FileManager.save_schedule(self.queue)

    def _find_project_by_id(self, id_str: str) -> Project | None:
        try:
            pid = int(id_str)
        except ValueError:
            return None
        return self.projects.get(pid)

    #  OPTION 1 – INPUT PROJECT

    def menu_input_project(self) -> None:
        header("1. Input Project Details")
        try:
            id_str = prompt("ID Number")
            id_number = validate_positive_int(id_str, "ID Number")
            if id_number in self.projects:
                print(f"\n  Error: Project ID {id_number} already exists.")
                pause()
                return

            title = validate_title(prompt("Title"))
            size = validate_positive_int(prompt("Size (pages)"), "Size")
            priority = validate_positive_int(prompt("Priority"), "Priority")
            due_date = validate_date(prompt("Due Date (YYYY-MM-DD)"))

        except ValidationError as e:
            print(f"\n  Validation Error: {e}")
            pause()
            return

        # Confirmation
        print()
        separator()
        print("  Project Details")
        separator()
        print(f"  ID       : {id_number}")
        print(f"  Title    : {title}")
        print(f"  Size     : {size}")
        print(f"  Priority : {priority}")
        print(f"  Due Date : {due_date}")
        separator()

        if confirm("Save this project? (Y/N)"):
            p = Project(id_number, title, size, priority, due_date)
            self.projects[id_number] = p
            self._rebuild_and_save_schedule()
            FileManager.save_projects(self.projects)
            print(f"\n  Project {id_number} saved successfully.")
        else:
            print("  Project not saved.")
        pause()

    #  OPTION 2 – EDIT PROJECT

    def menu_edit_project(self) -> None:
        header("2. Edit Project Details")
        id_str = prompt("Enter Project ID")
        p = self._find_project_by_id(id_str)
        if p is None:
            print("  Project not found.")
            pause()
            return

        print()
        display_project(p)
        separator()
        print("  Leave a field blank to keep current value.\n")

        try:
            raw = prompt(f"Title [{p.title}]")
            title = validate_title(raw) if raw else p.title

            raw = prompt(f"Size [{p.size}]")
            size = validate_positive_int(raw, "Size") if raw else p.size

            raw = prompt(f"Priority [{p.priority}]")
            priority = validate_positive_int(raw, "Priority") if raw else p.priority

            raw = prompt(f"Due Date [{p.due_date}]")
            due_date = validate_date(raw) if raw else p.due_date

            raw = prompt(f"Progress [{p.progress}]")
            progress = validate_non_negative_int(raw, "Progress", 100) if raw else p.progress

        except ValidationError as e:
            print(f"\n  Validation Error: {e}")
            pause()
            return

        if confirm("Update this project? (Y/N)"):
            p.title = title
            p.size = size
            p.priority = priority
            p.due_date = due_date
            p.progress = progress
            self._rebuild_and_save_schedule()
            FileManager.save_projects(self.projects)
            print(f"\n  Project {p.id_number} updated. Schedule regenerated.")
        else:
            print("  No changes saved.")
        pause()

    #  OPTION 3 – DELETE PROJECT

    def menu_delete_project(self) -> None:
        header("3. Delete Project")
        id_str = prompt("Enter Project ID")
        p = self._find_project_by_id(id_str)
        if p is None:
            print("  Project not found.")
            pause()
            return

        print()
        display_project(p)
        separator()

        if confirm("Are you sure you want to delete this project? (Y/N)"):
            del self.projects[p.id_number]
            self._rebuild_and_save_schedule()
            FileManager.save_projects(self.projects)
            print(f"\n  Project {p.id_number} deleted. Schedule updated.")
        else:
            print("  Deletion cancelled.")
        pause()

    #  OPTION 4 – UPDATE STATUS

    def menu_update_status(self) -> None:
        header("4. Update Project Status")
        id_str = prompt("Enter Project ID")
        p = self._find_project_by_id(id_str)
        if p is None:
            print("  Project not found.")
            pause()
            return

        print()
        display_project(p)
        separator()
        print("  Select Status:\n")
        print("    1. Pending")
        print("    2. In Progress")
        print("    3. Completed")

        choice = prompt("\n  Choice")
        status_map = {"1": "Pending", "2": "In Progress", "3": "Completed"}
        new_status = status_map.get(choice)
        if new_status is None:
            print("  Invalid choice.")
            pause()
            return

        if confirm(f"Set status to '{new_status}'? (Y/N)"):
            p.status = new_status
            if new_status == "Completed":
                p.progress = 100
            self._rebuild_and_save_schedule()
            FileManager.save_projects(self.projects)
            print(f"\n  Status updated to '{new_status}'. Schedule updated.")
        else:
            print("  No changes made.")
        pause()

    #  OPTION 5 – VIEW PROJECTS

    def menu_view_projects(self) -> None:
        while True:
            header("5. View Projects")
            print("  5.1  View One Project")
            print("  5.2  View Completed Projects")
            print("  5.3  View All Projects")
            print("  0    Back")
            separator()
            choice = prompt("Choice")
            if choice == "5.1":
                self._view_one()
            elif choice == "5.2":
                self._view_completed()
            elif choice == "5.3":
                self._view_all()
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")
                pause()

    def _view_one(self) -> None:
        header("5.1 View One Project")
        print("  Search by:")
        print("    1. ID")
        print("    2. Title")
        choice = prompt("Choice")

        p = None
        if choice == "1":
            p = self._find_project_by_id(prompt("Project ID"))
        elif choice == "2":
            term = prompt("Title (partial match)").lower()
            matches = [proj for proj in self.projects.values()
                    if term in proj.title.lower()]
            if len(matches) == 1:
                p = matches[0]
            elif len(matches) > 1:
                print(f"\n  {len(matches)} projects match. Showing first result.")
                p = matches[0]
        else:
            print("  Invalid choice.")
            pause()
            return

        if p is None:
            print("  Project not found.")
        else:
            print()
            separator()
            display_project(p)
            separator()
        pause()

    def _view_completed(self) -> None:
        header("5.2 Completed Projects")
        if not self.completed:
            print("  No completed projects yet.")
            pause()
            return

        fmt = "  {:<8} {:<6} {:<25} {:<8} {:<10} {:<12}"
        separator()
        print(fmt.format("CompDate", "ID", "Title", "Pages", "Priority", ""))
        separator()
        for cp in self.completed:
            print(fmt.format(
                str(cp.completion_date),
                cp.id_number,
                cp.title[:24],
                cp.size,
                cp.priority,
                ""
            ))
        separator()
        pause()

    def _view_all(self) -> None:
        header("5.3 All Projects")
        if not self.projects:
            print("  No projects on file.")
            pause()
            return

        print("  Sort by:  1. ID   2. Priority   3. Due Date   (Enter to skip)")
        choice = prompt("Choice")

        projects_list = list(self.projects.values())
        if choice == "1":
            projects_list.sort(key=lambda p: p.id_number)
        elif choice == "2":
            projects_list.sort(key=lambda p: p.priority)
        elif choice == "3":
            projects_list.sort(key=lambda p: p.due_date)

        fmt = "  {:<6} {:<25} {:<7} {:<9} {:<12} {:<5} {:<12}"
        print()
        separator()
        print(fmt.format("ID", "Title", "Size", "Priority", "Due Date", "Prog", "Status"))
        separator()
        for p in projects_list:
            print(fmt.format(
                p.id_number,
                p.title[:24],
                p.size,
                p.priority,
                str(p.due_date),
                f"{p.progress}%",
                p.status
            ))
        separator()
        pause()

    #  OPTION 6 – SCHEDULE

    def menu_schedule(self) -> None:
        while True:
            header("6. Schedule Projects")
            print("  6.1  Create Schedule")
            print("  6.2  View Schedule")
            print("  6.3  Schedule Statistics Dashboard")
            print("  6.4  Get Next Project")
            print("  0    Back")
            separator()
            choice = prompt("Choice")
            if choice == "6.1":
                self._create_schedule()
            elif choice == "6.2":
                self._view_schedule()
            elif choice == "6.3":
                self._dashboard()
            elif choice == "6.4":
                self._get_project()
            elif choice == "0":
                break
            else:
                print("  Invalid choice.")
                pause()

    def _create_schedule(self) -> None:
        header("6.1 Create Schedule")
        active = [p for p in self.projects.values() if p.status != "Completed"]
        if not active:
            print("  No active projects to schedule.")
            pause()
            return

        # Preview table
        preview = sorted(active, key=lambda p: (p.priority, p.due_date, p.size))
        fmt = "  {:<10} {:<12} {:<6}"
        print()
        separator()
        print(fmt.format("Priority", "Due Date", "Size"))
        separator()
        for p in preview:
            print(fmt.format(p.priority, str(p.due_date), p.size))
        separator()

        if confirm("Create schedule now? (Y/N)"):
            self._rebuild_and_save_schedule()
            print("\n  Schedule created and saved.\n")
            self._print_queue()
        else:
            print("  Schedule not created.")
        pause()

    def _print_queue(self) -> None:
        fmt = "  {:<10} {:<6} {:<25} {:<9} {:<12}"
        separator()
        print(fmt.format("Position", "ID", "Title", "Priority", "Due Date"))
        separator()
        for pos, pid in enumerate(self.queue, start=1):
            p = self.projects.get(pid)
            if p:
                print(fmt.format(pos, p.id_number, p.title[:24], p.priority, str(p.due_date)))
        separator()

    def _view_schedule(self) -> None:
        header("6.2 View Schedule")
        if not self.queue:
            print("  No schedule found.")
            print("  Please create a schedule first.")
            pause()
            return
        self._print_queue()
        pause()

    def _dashboard(self) -> None:
        header("6.3 Schedule Statistics Dashboard")
        total = len(self.projects)
        pending = sum(1 for p in self.projects.values() if p.status == "Pending")
        in_progress = sum(1 for p in self.projects.values() if p.status == "In Progress")
        completed_count = len(self.completed)
        pending_pages = sum(
            p.size for p in self.projects.values()
            if p.status in ("Pending", "In Progress")
        )
        avg_size = (pending_pages // (pending + in_progress)
                    if (pending + in_progress) > 0 else 0)

        active = [p for p in self.projects.values() if p.status != "Completed"]
        highest_priority_proj = min(active, key=lambda p: p.priority) if active else None
        nearest_due_proj = min(active, key=lambda p: p.due_date) if active else None
        queue_len = len(self.queue)

        separator("═")
        print("  ===== DASHBOARD =====")
        separator("═")
        print(f"  Total Projects       : {total}")
        print(f"  Pending Projects     : {pending}")
        print(f"  In Progress          : {in_progress}")
        print(f"  Completed Projects   : {completed_count}")
        print(f"  Total Pages Pending  : {pending_pages:,}")
        print(f"  Average Project Size : {avg_size} pages")
        print()
        if highest_priority_proj:
            print(f"  Highest Priority Project:")
            print(f"    ID {highest_priority_proj.id_number} – {highest_priority_proj.title}")
        else:
            print("  Highest Priority Project: N/A")
        print()
        if nearest_due_proj:
            print(f"  Nearest Due Date:")
            print(f"    ID {nearest_due_proj.id_number} – {nearest_due_proj.title}")
            print(f"    Due: {nearest_due_proj.due_date}")
        else:
            print("  Nearest Due Date: N/A")
        print()
        print(f"  Current Queue Length : {queue_len}")
        separator("═")
        pause()

    def _get_project(self) -> None:
        header("6.4 Get Next Project")
        if not self.queue:
            print("  Queue is empty. No projects to process.")
            pause()
            return

        self._print_queue()
        next_id = self.queue[0]
        p = self.projects.get(next_id)
        if p is None:
            print("  Error: front of queue references a missing project.")
            self._clean_queue()
            pause()
            return

        if confirm("Start and complete this project? (Y/N)"):
            # Remove from queue
            self.queue.popleft()
            # Save to completed
            cp = CompletedProject(
                p.id_number, p.title, p.size,
                p.priority, p.due_date, date.today()
            )
            self.completed.append(cp)
            FileManager.save_completed(self.completed)
            # Remove from active projects
            del self.projects[p.id_number]
            # Update files
            FileManager.save_projects(self.projects)
            FileManager.save_schedule(self.queue)

            print(f"\n  Project {p.id_number} completed successfully.\n")
            if self.queue:
                print("  Queue Updated:")
                self._print_queue()
            else:
                print("  Queue is now empty.")
        else:
            print("  No action taken.")
        pause()

    #  MAIN MENU

    def main_menu(self) -> None:
        while True:
            clear()
            header("PROJECT QUEUE MANAGEMENT SYSTEM", 55)
            print("  1.  Input Project Details")
            print("  2.  Edit Project Details")
            print("  3.  Delete Project")
            print("  4.  Update Project Status")
            print("  5.  View Projects")
            print("  6.  Schedule Projects")
            print("  7.  Exit")
            separator()
            choice = prompt("Choice")

            actions = {
                "1": self.menu_input_project,
                "2": self.menu_edit_project,
                "3": self.menu_delete_project,
                "4": self.menu_update_status,
                "5": self.menu_view_projects,
                "6": self.menu_schedule,
            }

            if choice in actions:
                actions[choice]()
            elif choice == "7":
                if confirm("Are you sure you want to exit? (Y/N)"):
                    print("\n  Goodbye!\n")
                    sys.exit(0)
            else:
                print("  Invalid choice. Please enter 1–7.")
                pause()

# MAIN

if __name__ == "__main__":
    try:
        app = App()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\n  Interrupted. Exiting.")
        sys.exit(0)
