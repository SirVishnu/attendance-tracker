# Attendance Tracker

#### Description:
A personal attendance tracking web application built with flask and sqlite.
Track your lecture attendance across multiple groups and subjects. [Site link][https://sovietgeneral.pythonanywhere.com/]


## Features

- User authentication (register, login, logout)
- Create groups (e.g. college, course name)
- Optional subjects/subgroups inside each group
- Track lectures conducted vs lectures attended per day
- Attendance percentage calculated automatically

## Tech Stack

- **Backend** — Python, Flask
- **Database** — SQLite
- **Frontend** — HTML, CSS



## Usage

1. Register an account
2. Create a group (e.g. "TSEC SEM 1")
3. Choose whether the group has subjects or not
4. If yes, add subjects inside the group
5. Add lectures — enter date (by default today's date), lectures conducted, lectures attended
6. View attendance percentage on the group or subject page

## Note

- Attendance percentage = (lectures attended / lectures conducted) * 100
- Deleting a group removes all its subjects and sessions automatically
- Deleting a subject removes all its sessions automatically

[https://sovietgeneral.pythonanywhere.com/]: https://sovietgeneral.pythonanywhere.com/