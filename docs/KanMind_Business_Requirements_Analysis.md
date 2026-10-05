# KanMind Business Requirements Analysis

> This document explains the main business requirements of the KanMind backend in simple English.  
> The goal is to understand the product before making technical decisions with Django and Django REST Framework.

---

## 1. Product Overview

**KanMind** is a project and task management tool based on the **Kanban** idea, similar to Trello.

Users can:

- create Boards,
- add Members to Boards,
- create and manage Tasks,
- assign Tasks to users,
- choose a Reviewer,
- move Tasks through different Status values,
- write Comments on Tasks,
- see only Boards and Tasks that are related to them,
- use the Dashboard to get an overview of their work.

---

## 2. Problem Statement

KanMind helps teams organize their work in one place.

The main problem is:

> Team members need a shared system to organize Tasks, assign responsibility, review work, track progress, and communicate about Tasks.

KanMind organizes this information with:

```text
Board
└── Task
    └── Comment
```

---

## 3. Actors

### 3.1 User

A **User** is a registered person who can log in to the system.

A User can have different roles depending on the Board or Task:

- Board Owner
- Board Member
- Task Assignee
- Task Reviewer
- Comment Author

A User does not have to be a Member of every Board in the system.

### 3.2 Board Owner

The User who creates a Board becomes the `owner` of that Board.

The Owner has more permissions than a normal Member.

For example, only the Owner can delete a Board.

### 3.3 Board Member

A User can be a Member of a Board.

Board membership is important because many Task and Comment actions require the User to be a Member of that Board.

### 3.4 Guest User

The project introduction mentions a **Guest User**.

The exact Backend behavior is not clear yet.

Open questions:

- Is Guest a real User in the database?
- Is Guest only a prepared demo account?
- Does Guest use the normal login endpoint?
- Does Guest have special permissions?

We should not invent Guest behavior until the official project sources define it.

---

## 4. Main Domain Entities

### 4.1 User

Important User information:

- `id`
- `fullname`
- `email`
- authentication data

### 4.2 Board

A Board is the main place where work is organized.

Important Board information:

- `id`
- `title`
- `owner`
- `members`
- related Tasks

### 4.3 Task

A Task is the main work item in KanMind.

Important Task information:

- `id`
- `board`
- `title`
- `description`
- `status`
- `priority`
- `assignee`
- `reviewer`
- `due_date`
- `comments_count`

### 4.4 Comment

A Comment belongs to a Task.

Important Comment information:

- `id`
- `created_at`
- `author`
- `content`
- related Task

---

## 5. Entity Relationships

```text
User
├── owns Board(s)
├── is Member of Board(s)
├── can be Assignee of Task(s)
├── can be Reviewer of Task(s)
└── can be Author of Comment(s)

Board
└── contains Task(s)

Task
└── contains Comment(s)
```

Important notes:

- A Board can have many Members.
- A Board can have many Tasks.
- Every Task belongs to one Board.
- A Task can have an Assignee and a Reviewer.
- Every Comment belongs to one Task.
- The Comment Author comes from the authenticated User.

> This section describes the business relationships only.  
> It does not decide yet if Django should use `ForeignKey`, `ManyToManyField`, or another technical solution.

---

## 6. Main Workflows

### 6.1 Authentication Flow

```text
Register
↓
Login
↓
Receive Token
↓
Use authenticated API endpoints
```

### 6.2 Board Flow

```text
Authenticated User
↓
Create Board
↓
User becomes Owner
↓
Add Members
↓
Create and manage Tasks
```

### 6.3 Task Workflow

A Task can use these Status values:

```text
to-do
↓
in-progress
↓
review
↓
done
```

The frontend shows these values as Kanban columns.

### 6.4 Comment Flow

```text
Board Member
↓
Open Task
↓
Create Comment
↓
Authenticated User becomes Author
```

---

## 7. Business Rules

A **Business Rule** is a rule that defines what is allowed or not allowed in the system.

### 7.1 Board Rules

- A User must be authenticated to create a Board.
- The User who creates a Board automatically becomes the Owner.
- A User can only see Boards where they are the Owner or a Member.
- Only the Owner can delete a Board.

### 7.2 Task Rules

- Every Task belongs to a Board.
- Only Board Members can create Tasks in that Board.
- The `assignee` must be a Member of the same Board.
- The `reviewer` must be a Member of the same Board.
- `assignee` and `reviewer` can be empty.
- `status` must be one of:

```text
to-do
in-progress
review
done
```

- `priority` must be one of:

```text
low
medium
high
```

- The Board of a Task must not be changed during Task update.
- Task deletion must follow the official permission rules.

### 7.3 Comment Rules

- Every Comment belongs to a Task.
- Only Members of the related Board can create Comments.
- The Comment Author is the authenticated User.
- Comments are returned in chronological order.
- Only the Author of a Comment can delete it.

---

## 8. Dashboard Requirements

The Dashboard is not necessarily a separate Backend entity.

It mainly shows information that already exists in Boards and Tasks.

The Dashboard can show:

- Boards related to the User,
- Tasks assigned to the User,
- Tasks where the User is Reviewer,
- number of Tasks by Status,
- Priority,
- Due Date,
- Comment Count,
- completed Tasks,
- next important Tasks.

> A page in the frontend does not always need its own Model in the Backend.

---

## 9. Functional Requirements

### Authentication

- User can register.
- User can log in with Email and Password.
- Backend returns an authentication Token.

### Boards

- User can see accessible Boards.
- User can create a Board.
- Members can be added or removed.
- Board details can include related Tasks.
- Board deletion follows the official permissions.

### Tasks

- User can see Tasks assigned to them.
- User can see Tasks where they are Reviewer.
- Board Members can create Tasks.
- Board Members can update allowed Task fields.
- Task deletion follows the official permissions.

### Comments

- Board Members can see Comments of a Task.
- Board Members can create Comments.
- Comment Author can delete their own Comment.

---

## 10. Project Constraints

These rules come from the project requirements:

- Backend must have its own Git repository.
- Frontend must not be included in the Backend repository.
- The official API Endpoint Documentation is the source of truth.
- URL, HTTP Method, Request, Response, Status Codes, and Permissions must match the documentation.
- Target Postman test success is 100%.
- Minimum required success is 95%.
- Database files must not be committed.
- Secrets must not be committed.
- Final README must be written in English.
- `requirements.txt` must stay complete and up to date.

---

## 11. Requirement vs Technical Implementation

It is important to separate **what the system must do** from **how we implement it**.

| Requirement | Possible Technical Implementation |
|---|---|
| Only Owner can delete a Board | DRF Permission |
| Assignee must be a Board Member | Serializer Validation |
| Task belongs to a Board | Model Relationship |
| Some endpoints require login | Authentication and Permission |
| Task Status has only four allowed values | Choices or Validation |

> During Business Analysis, focus first on the Requirement.  
> Technical decisions come later during Architecture and Implementation.

---

## 12. Open Questions

These points still need to be checked in the official project sources:

- What exactly is the Guest User?
- Does Guest use a normal User account?
- Does Guest have special permissions?
- Can a Member add or remove other Members, or only the Owner?
- Can a Task move directly from `to-do` to `done`, or must it follow the full order?
- Can a Comment be edited?
- Does the Owner also need to be a Board Member, or are Owner and Member separate roles?

> If the official documentation does not answer a question, we should not invent Backend behavior.

---

## 13. Source of Truth

For this project, use this order:

1. Official API Endpoint Documentation
2. KanMind Backend Master Checklist
3. Official Django/DRF Project Checklist
4. Project Introduction / Demo Videos
5. Frontend for integration testing

If the Frontend or Video is different from the official API Documentation, the **API Documentation has priority**.

---

## 14. Analysis Method for Future Projects

A useful analysis order is:

```text
Problem
↓
Actors
↓
Entities
↓
Relationships
↓
Main Workflows
↓
Business Rules
↓
Permissions
↓
Open Questions
↓
API Contract
↓
Technical Architecture
```

Questions to ask:

- What problem does the product solve?
- Who uses the system?
- What roles exist?
- What are the main Entities?
- How are the Entities related?
- What is the main Workflow?
- What Business Rules exist?
- Who can do which Action?
- What is not allowed?
- What is still unclear?
- What is the Source of Truth?
- What is a Requirement and what is only an Implementation idea?

---

## 15. Current Understanding

KanMind is a collaborative Kanban task management system.

Users work together inside Boards, create and manage Tasks, assign Tasks to team members, choose Reviewers, move Tasks through different Status values, and communicate through Comments.

This file is **living documentation** and can be updated when we learn more about the project.
