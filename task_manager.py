"""
Task manager for a small business team.

Stores users in user.txt and tasks in tasks.txt, one record per line
with fields separated by a comma and a space. Allows users to log in,
add and view tasks, mark their own tasks complete or edit them, and
generate reports. Admin users can also register users, view completed
tasks and delete tasks.
"""

from datetime import datetime

USERS_FILE = "user.txt"
TASKS_FILE = "tasks.txt"
DISPLAY_FORMAT = "%d %b %Y"
INPUT_FORMAT = "%d/%m/%Y"
ADMIN_ONLY_OPTIONS = ('r', 'vc', 'del')
TASK_OVERVIEW_FILE = "task_overview.txt"
USER_OVERVIEW_FILE = "user_overview.txt"

ADMIN_MENU = '''Select one of the following options:
r - register a user
a - add task
va - view all tasks
vm - view my tasks
vc - view completed tasks
del - delete a task
ds - display statistics
gr - generate reports
e - exit
: '''

USER_MENU = '''Select one of the following options:
a - add task
va - view all tasks
vm - view my tasks
ds - display statistics
gr - generate reports
e - exit
: '''


class Task:
    """
        A single task, matching the six fields stored per line in tasks.txt.

        Dates are held as strings in the display format, and
        completion_status as the string "Yes" or "No", so a Task maps
        directly onto a line of the file.
        """
    def __init__(self, assigned_to, task_title, task_description,
                 date_assigned, date_due, completion_status="No"):
        self.assigned_to = assigned_to
        self.task_title = task_title
        self.task_description = task_description
        self.date_assigned = date_assigned
        self.date_due = date_due
        self.completion_status = completion_status

    def __str__(self):
        return (f"{'Task:':<20}{self.task_title}\n"
                f"{'Assigned to:':<20}{self.assigned_to}\n"
                f"{'Description:':<20}{self.task_description}\n"
                f"{'Date assigned:':<20}{self.date_assigned}\n"
                f"{'Date due:':<20}{self.date_due}\n"
                f"{'Completion status:':<20}{self.completion_status}\n")

    def is_complete(self):
        return self.completion_status.lower() == "yes"

    def is_overdue(self):
        """
                Report whether this task is past its due date and not complete.

                A completed task is never overdue. If the due date in the file
                cannot be read as a date, the task is treated as not overdue
                instead of crashing, since the file can be edited by hand.
                A task due today is not yet overdue.

                :return: True if the task is incomplete and past due
                """
        if self.is_complete():
            return False
        try:
            due = datetime.strptime(self.date_due, DISPLAY_FORMAT).date()
        except ValueError:
            return False
        return due < datetime.today().date()


def display_tasks(tasks):
    """
    Print a numbered list of tasks to the screen.

    The numbers start at 1 and match the position in the list passed
    in, so a caller can use them to let the user select a task.

    :param tasks: list of Task objects to print
    :return: None
    """
    for index, task in enumerate(tasks):
        print(f" ----- TASK {index + 1} -----")
        print(task)


def load_users():
    """
    Read user.txt and build a dictionary of usernames and passwords.

    Blank lines are skipped. If the file is missing the program stops,
    since nobody could log in without it.

    :return: dict mapping each username to its password
    """
    login_details = {}
    try:
        with open(USERS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                # Skip blank lines left behind by hand-editing.
                if not line:
                    continue
                username, password = line.split(", ")
                login_details[username] = password
    except FileNotFoundError:
        print(f"Error: {USERS_FILE} was not found. "
              f"The program cannot run without it.")
        raise SystemExit(1)
    return login_details


def login(login_details):
    """
    Prompt for a username and password until a valid pair is entered.

    The username is checked first, so the password comparison below it
    can safely look up the username in the dictionary.

    :param login_details: dict mapping username to password
    :return: the username of the user who logged in
    """
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if username not in login_details:
            print("Invalid username, try again.")
        elif password != login_details[username]:
            print("Incorrect password, try again.")
        else:
            print("Login successful.")
            return username


def save_users(login_details):
    """
    Write every registered user back to the users file.

    The whole file is rewritten, so a missing final newline in the
    existing file cannot join two users onto one line.

    :param login_details: dict mapping username to password
    :return: None
    """
    with open(USERS_FILE, "w") as f:
        for username, password in login_details.items():
            f.write(f"{username}, {password}\n")


def reg_user(login_details):
    """
    Add a new user to the users file and to the in-memory dictionary.

    Usernames must be unique and free of commas. Passwords must be
    confirmed, and must contain no commas and no trailing whitespace,
    since the file format cannot preserve either.

    :param login_details: dict mapping username to password
    :return: None
    """
    while True:
        new_username = input(
            "Please enter a username for the new user: ").strip()
        if not new_username:
            print("The username cannot be blank, please try again.")
            continue
        if "," in new_username:
            print("Usernames cannot contain commas, please try again.")
            continue
        if new_username in login_details:
            print("This username is taken, please enter a unique username.")
            continue

        while True:
            new_password = input("Please enter a password for the new user: ")
            if not new_password.strip():
                print("The password cannot be blank, please try again.")
                continue
            if "," in new_password:
                print("Passwords cannot contain commas, please try again.")
                continue
            if new_password != new_password.rstrip():
                print("Passwords cannot end in a space, please try again.")
                continue
            confirm_new_password = input("Please confirm the password: ")
            if new_password == confirm_new_password:
                break
            print("The passwords did not match, please try again.")
        break

    login_details[new_username] = new_password
    save_users(login_details)
    print(f"The new user has been added with the following details:\n"
          f"Username: {new_username}\n"
          f"Password: {new_password}")


def load_tasks():
    """
    Read tasks.txt and build a list of Task objects, one per line.

    Blank lines are skipped. If the file is missing an empty one is
    created and the program carries on, since having no tasks yet is
    normal.

    :return: list of Task objects
    """
    tasks = []
    try:
        with open(TASKS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                (assigned_to, task_title, task_description,
                 date_assigned, date_due, completion_status) = line.split(", ")
                tasks.append(Task(assigned_to, task_title,
                                  task_description, date_assigned,
                                  date_due, completion_status))
    except FileNotFoundError:
        print(f"{TASKS_FILE} was not found. Starting with no tasks.")
        with open(TASKS_FILE, "w"):
            pass
    return tasks


def save_tasks(task_list):
    """
    Write every task back to the tasks file.

    The whole file is rewritten rather than appended to, so this also
    handles tasks being edited or deleted. The field order must match
    what load_tasks expects.

    :param task_list: list of Task objects
    :return: None
    """
    with open(TASKS_FILE, "w") as f:
        for task in task_list:
            f.write(f"{task.assigned_to}, {task.task_title}, "
                    f"{task.task_description}, {task.date_assigned}, "
                    f"{task.date_due}, {task.completion_status}\n")


def add_task(login_details, task_list):
    """
    Collect the details of a new task and save it.

    The task is assigned today's date and a completion status of "No".
    Commas are rejected in the title and description because they are
    the separator used in tasks.txt. The task list is updated in place,
    so the caller sees the new task without anything being returned.

    :param login_details: dict mapping username to password
    :param task_list: list of Task objects, appended to in place
    :return: None
    """
    while True:
        new_assigned_to = input("Enter the username of the staff "
                                "member this job is assigned to: ").strip()
        if new_assigned_to in login_details:
            break
        print("You have entered an invalid username,"
              " please try again.")

    while True:
        new_task_title = input("Enter the title of the task: ").strip()
        if not new_task_title:
            print("The title cannot be blank, please try again.")
            continue
        if "," in new_task_title:
            print("The title cannot contain commas, please try again.")
            continue
        break

    while True:
        new_task_description = input(
            "Enter a description for the task: ").strip()
        if not new_task_description:
            print("The description cannot be blank, please try again.")
            continue
        if "," in new_task_description:
            print("The description cannot contain commas, "
                  "please try again.")
            continue
        break

    date_assigned = datetime.today().strftime(DISPLAY_FORMAT)

    while True:
        date_due = input("Enter the due date (DD/MM/YYYY): ")
        try:
            parsed_date = datetime.strptime(date_due, INPUT_FORMAT)
            date_due = parsed_date.strftime(DISPLAY_FORMAT)
            break
        except ValueError:
            print("Invalid date format, please use DD/MM/YYYY.")

    new_task = Task(new_assigned_to, new_task_title, new_task_description,
                    date_assigned, date_due)

    task_list.append(new_task)
    save_tasks(task_list)
    print(f"Task '{new_task_title}' has been assigned to {new_assigned_to}.")


def view_all(task_list):
    """
    Print every task in the system, or a message if there are none.

    :param task_list: list of Task objects
    :return: None
    """
    if not task_list:
        print("There are no tasks.")
        return
    display_tasks(task_list)


def select_task_number(tasks):
    """
    Prompt until the user picks a valid task number or cancels.

    The number returned is the one shown on screen, starting at 1, so
    the caller subtracts 1 to index the list. Cancelling returns None
    rather than -1, so the caller does not need to know which input
    means cancel.

    :param tasks: the list of Task objects being chosen from
    :return: the chosen task number, or None if the user cancelled
    """
    while True:
        selection = input("Enter the number of a task to select it, "
                          "or -1 to return to the main menu: ")
        try:
            task_number = int(selection)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if task_number == -1:
            return None
        if 1 <= task_number <= len(tasks):
            return task_number
        print(f"Please enter a number between 1 and {len(tasks)}.")


def mark_task_complete(task, task_list):
    """
    Mark a task as complete and save the change to file.

    The task is modified in place, so it must be one of the objects in
    task_list rather than a copy, or the saved file will not match.

    :param task: the Task to mark complete
    :param task_list: the full list of Task objects, saved afterwards
    :return: None
    """
    if task.is_complete():
        print("That task is already complete.")
        return
    task.completion_status = "Yes"
    save_tasks(task_list)
    print(f"Task '{task.task_title}' has been marked as complete.")


def edit_task(task, task_list, login_details):
    """
    Change the assignee or due date of a task that is not yet complete.

    Both fields are offered. Pressing Enter at either prompt leaves
    that field unchanged, so the user can edit one or both. The task is
    modified in place, so it must be one of the objects in task_list
    rather than a copy, or the saved file will not match.

    :param task: the Task to edit
    :param task_list: the full list of Task objects, saved afterwards
    :param login_details: dict mapping username to password, used to
                          check that a new assignee exists
    :return: None
    """

    if task.is_complete():
        print("Completed tasks cannot be edited.")
        return

    new_assigned_to = input("Enter a new username to reassign this task, "
                            "or press Enter to keep it unchanged: ").strip()
    if new_assigned_to:
        if new_assigned_to in login_details:
            task.assigned_to = new_assigned_to
        else:
            print("That username does not exist. "
                  "The task was not reassigned.")

    new_date_due = input("Enter a new due date (DD/MM/YYYY), "
                         "or press Enter to keep it unchanged: ").strip()
    if new_date_due:
        try:
            parsed_date = datetime.strptime(new_date_due, INPUT_FORMAT)
            task.date_due = parsed_date.strftime(DISPLAY_FORMAT)
        except ValueError:
            print("Invalid date format. The due date was not changed.")

    save_tasks(task_list)
    print("The task has been updated.")


def view_mine(current_user, task_list, login_details):
    """
    Show the current user's tasks and let them act on one.

    The tasks are numbered from 1, and the user can pick one to mark
    complete or edit, or return to the menu. Only one action is taken
    before returning, so the user comes back through the menu to act
    on another task.

    :param current_user: username of the logged-in user
    :param task_list: full list of Task objects, passed on to the
                      functions that save changes
    :param login_details: dict mapping username to password, needed to
                          validate a new assignee when editing
    :return: None
    """
    current_users_tasks = [task for task in task_list
                           if task.assigned_to == current_user]
    if not current_users_tasks:
        print("You have no tasks assigned to you.")
        return

    display_tasks(current_users_tasks)

    task_number = select_task_number(current_users_tasks)
    if task_number is None:
        return

    selected_task = current_users_tasks[task_number - 1]
    print(selected_task)

    while True:
        action = input("Enter 'c' to mark this task complete, 'e' to edit "
                       "it, or -1 to return to the main menu: ")
        action = action.strip().lower()
        if action == "-1":
            return
        if action == "c":
            mark_task_complete(selected_task, task_list)
            return
        if action == "e":
            edit_task(selected_task, task_list, login_details)
            return
        print("Invalid input, please try again.")


def view_completed(task_list):
    """
    Print every completed task, or a message if there are none.

    :param task_list: list of Task objects
    :return: None
    """
    completed_tasks = [task for task in task_list if task.is_complete()]
    if not completed_tasks:
        print("There are no completed tasks.")
        return
    display_tasks(completed_tasks)


def delete_task(task_list):
    """
    Show all tasks and delete the one the user selects.

    The task is removed from task_list in place and the whole file is
    rewritten, since a single line cannot be removed from a file. There
    is no confirmation step, but the user can cancel before choosing.

    :param task_list: full list of Task objects, modified in place
    :return: None
    """
    if not task_list:
        print("There are no tasks to delete.")
        return

    display_tasks(task_list)

    task_number = select_task_number(task_list)
    if task_number is None:
        return

    deleted_task = task_list.pop(task_number - 1)
    save_tasks(task_list)
    print(f"Task '{deleted_task.task_title}' has been deleted.")


def get_task_statistics(task_list):
    """
    Calculate overall statistics across every task in the system.

    Percentages are returned as 0 when there are no tasks, rather than
    raising ZeroDivisionError.

    :param task_list: list of Task objects
    :return: dict with the keys total_tasks, completed_tasks,
             uncompleted_tasks, overdue_tasks, percentage_incomplete
             and percentage_overdue
    """
    total_tasks = len(task_list)
    completed_tasks = len([task for task in task_list if task.is_complete()])
    overdue_tasks = len([task for task in task_list if task.is_overdue()])
    uncompleted_tasks = total_tasks - completed_tasks

    if total_tasks:
        percentage_incomplete = uncompleted_tasks / total_tasks * 100
        percentage_overdue = overdue_tasks / total_tasks * 100
    else:
        percentage_incomplete = 0
        percentage_overdue = 0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "uncompleted_tasks": uncompleted_tasks,
        "overdue_tasks": overdue_tasks,
        "percentage_incomplete": percentage_incomplete,
        "percentage_overdue": percentage_overdue,
    }


def get_user_statistics(login_details, task_list):
    """
    Calculate task statistics for the system and for each registered user.

    Every registered user is included, even one with no tasks assigned.
    Percentages are returned as 0 where the relevant total is zero.

    :param login_details: dict mapping username to password
    :param task_list: list of Task objects
    :return: dict with the keys total_users, total_tasks and users, where
             users maps each username to a dict with the keys
             assigned_count, percentage_of_all, percentage_completed,
             percentage_uncompleted and percentage_overdue
    """
    total_users = len(login_details)
    total_tasks = len(task_list)
    user_statistics = {}

    for username in login_details:
        assigned = [task for task in task_list
                    if task.assigned_to == username]
        assigned_count = len(assigned)
        completed_count = len([task for task in assigned
                               if task.is_complete()])
        overdue_count = len([task for task in assigned
                             if task.is_overdue()])
        uncompleted_count = assigned_count - completed_count

        if total_tasks:
            percentage_of_all = assigned_count / total_tasks * 100
        else:
            percentage_of_all = 0

        if assigned_count:
            percentage_completed = completed_count / assigned_count * 100
            percentage_uncompleted = uncompleted_count / assigned_count * 100
            percentage_overdue = overdue_count / assigned_count * 100
        else:
            percentage_completed = 0
            percentage_uncompleted = 0
            percentage_overdue = 0

        user_statistics[username] = {
            "assigned_count": assigned_count,
            "percentage_of_all": percentage_of_all,
            "percentage_completed": percentage_completed,
            "percentage_uncompleted": percentage_uncompleted,
            "percentage_overdue": percentage_overdue,
        }

    return {
        "total_users": total_users,
        "total_tasks": total_tasks,
        "users": user_statistics,
    }


def build_task_overview(stats):
    """
    Format the overall task statistics as text for display or writing.

    :param stats: dict as returned by get_task_statistics
    :return: the formatted report as a single string
    """
    return (f"{'TASK OVERVIEW':-^50}\n"
            f"{'Total tasks:':<30}{stats['total_tasks']}\n"
            f"{'Completed tasks:':<30}{stats['completed_tasks']}\n"
            f"{'Uncompleted tasks:':<30}{stats['uncompleted_tasks']}\n"
            f"{'Overdue tasks:':<30}{stats['overdue_tasks']}\n"
            f"{'Percentage incomplete:':<30}"
            f"{stats['percentage_incomplete']:.1f}%\n"
            f"{'Percentage overdue:':<30}"
            f"{stats['percentage_overdue']:.1f}%\n"
            f"{'':-^50}\n")


def build_user_overview(stats):
    """
    Format the user statistics as text, with one block per user.

    :param stats: dict as returned by get_user_statistics
    :return: the formatted report as a single string
    """
    lines = [f"{'USER OVERVIEW':-^50}\n",
             f"{'Total users:':<30}{stats['total_users']}\n",
             f"{'Total tasks:':<30}{stats['total_tasks']}\n"]

    for username, user_stats in stats["users"].items():
        heading = f" {username} "
        lines.append(f"\n{heading:-^50}\n")
        lines.append(f"{'Tasks assigned:':<30}"
                     f"{user_stats['assigned_count']}\n")
        lines.append(f"{'Percentage of all tasks:':<30}"
                     f"{user_stats['percentage_of_all']:.1f}%\n")
        lines.append(f"{'Percentage completed:':<30}"
                     f"{user_stats['percentage_completed']:.1f}%\n")
        lines.append(f"{'Percentage to complete:':<30}"
                     f"{user_stats['percentage_uncompleted']:.1f}%\n")
        lines.append(f"{'Percentage overdue:':<30}"
                     f"{user_stats['percentage_overdue']:.1f}%\n")

    lines.append(f"{'':-^50}\n")
    return "".join(lines)


def generate_reports(login_details, task_list):
    """
    Write the task and user overview reports to their text files.

    Any existing reports are overwritten with current figures.

    :param login_details: dict mapping username to password
    :param task_list: list of Task objects
    :return: None
    """
    task_stats = get_task_statistics(task_list)
    user_stats = get_user_statistics(login_details, task_list)

    with open(TASK_OVERVIEW_FILE, "w") as f:
        f.write(build_task_overview(task_stats))

    with open(USER_OVERVIEW_FILE, "w") as f:
        f.write(build_user_overview(user_stats))

    print(f"Reports generated: {TASK_OVERVIEW_FILE} "
          f"and {USER_OVERVIEW_FILE}.")


def read_report(filename):
    """
    Read the full contents of a report file.

    :param filename: path of the report file to read
    :return: the file's contents as a single string
    """
    with open(filename, "r") as f:
        return f.read()


def display_statistics(login_details, task_list):
    """
    Print the task and user overview reports to the screen.

    The reports are regenerated first so the figures shown are current.

    :param login_details: dict mapping username to password
    :param task_list: list of Task objects
    :return: None
    """
    generate_reports(login_details, task_list)
    print(read_report(TASK_OVERVIEW_FILE), end="")
    print(read_report(USER_OVERVIEW_FILE), end="")


login_details = load_users()
current_user = login(login_details)
task_list = load_tasks()

is_admin = current_user == "admin"
current_menu = ADMIN_MENU if is_admin else USER_MENU

# ===== Main program =====

while True:
    menu = input(current_menu).strip().lower()

    if menu in ADMIN_ONLY_OPTIONS and not is_admin:
        print("That option is only available to the admin.")
        continue

    if menu == 'r':
        reg_user(login_details)
    elif menu == 'a':
        add_task(login_details, task_list)
    elif menu == 'va':
        view_all(task_list)
    elif menu == 'vm':
        view_mine(current_user, task_list, login_details)
    elif menu == 'vc':
        view_completed(task_list)
    elif menu == 'del':
        delete_task(task_list)
    elif menu == 'ds':
        display_statistics(login_details, task_list)
    elif menu == 'gr':
        generate_reports(login_details, task_list)
    elif menu == 'e':
        print('Goodbye!!!')
        break
    else:
        print("You have entered an invalid input. Please try again.")