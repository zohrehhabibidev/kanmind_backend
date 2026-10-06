# KanMind Model Requirements — Card 06

> Purpose: Derive the data structure, relationships, required/optional information, and business rules from the official KanMind API documentation **before implementing Django models**.
>
> Scope: `User`, `Board`, `Task`, `Comment`
>
> Important: The official API documentation is the source of truth. Where requiredness is not stated explicitly, this document marks it as **Not explicitly specified** instead of guessing.

---

## 1. User Requirements

> The User model is provided/expected by the project context. Do not invent a separate authentication model.

| Item | Classification | Required / Optional | Notes |
|---|---|---|---|
| `id` | Model data | System-generated | Unique user identifier returned by the API as `user_id` or `id`. |
| `fullname` | Model data | Appears in registration request; explicit requiredness not stated | Used in user representations throughout the API. |
| `email` | Model data | Appears in registration/login requests; explicit requiredness not stated | Used for login and email lookup. |
| `password` | Authentication-related model data | Appears in registration/login requests; explicit requiredness not stated | Must be handled by the provided Django user/authentication system. |
| `repeated_password` | API-only validation data | Registration only | Used to compare against `password`; not persistent model data. |
| `token` | Authentication data, not a direct User model field | Returned after registration/login | Managed through DRF token authentication; do not add a custom `token` field to User. |

### User Relationships

| Related Model | Relationship Role |
|---|---|
| `Board` | A User can be a board `owner`. |
| `Board` | A User can be one of multiple board `members`. |
| `Task` | A User can be a task `assignee`. |
| `Task` | A User can be a task `reviewer`. |
| `Task` | The system must know the task `creator` because task deletion depends on it. The exact field name is not specified by the API documentation. |
| `Comment` | A User is the `author` of a comment. |

---

## 2. Board Requirements

### Board Data and Relationships

| Item | Classification | Cardinality / Source | Required / Optional | Notes |
|---|---|---|---|---|
| `id` | Model data | System-generated | System-generated | Board identifier. |
| `title` | Model data | Board | Not explicitly specified | Appears in create/update requests and responses. |
| `owner` | Relationship | Exactly one User | Assigned automatically | The authenticated creator becomes the owner. Client does not send the owner. |
| `members` | Relationship | Multiple Users | Not explicitly specified | Create/update requests use a list of user IDs. The owner may also be included as a member. |
| `tasks` | Relationship | Multiple Tasks | Derived from related Tasks | Returned in board detail responses. |
| `member_count` | Calculated | From `members` | API-calculated | Number of board members. |
| `ticket_count` | Calculated | From related Tasks | API-calculated | Total number of Tasks on the Board. The API uses the name `ticket_count`. |
| `tasks_to_do_count` | Calculated | From related Tasks | API-calculated | Count of Tasks whose status is `to-do`. |
| `tasks_high_prio_count` | Calculated | From related Tasks | API-calculated | Count of Tasks whose priority is `high`. |

### API Representation Notes

| API Field | Meaning |
|---|---|
| `owner_id` | ID-only representation of the Board owner. |
| `owner_data` | Expanded representation of the same Board owner. |
| `members` | Member representation used by some endpoints. |
| `members_data` | Expanded representation of the same Board members. |

These are different API representations of the same underlying relationships, not separate model relationships.

### Board Business Rules

| Rule | Requirement |
|---|---|
| Create Board | Authenticated user is required. |
| Owner assignment | The authenticated user who creates the Board becomes its owner automatically. |
| Owner membership | The owner may also appear in the Board's members list. |
| Read Board list | A user only receives Boards they own or belong to as a member. |
| Read Board detail | User must be the owner or a member. |
| Update Board | Owner or member may update the Board. |
| Board update scope | Board update is for Board data/members, not Task updates. |
| Members update behavior | The submitted members list replaces the previous membership set; omitted previous members are removed. |
| Delete Board | Only the Board owner may delete it. |
| Delete cascade | Deleting a Board removes its related Tasks and Comments. |

---

## 3. Task Requirements

### Task Data and Relationships

| Item | Classification | Cardinality / Source | Required / Optional | Notes |
|---|---|---|---|---|
| `id` | Model data | System-generated | System-generated | Task identifier. |
| `board` | Relationship | Exactly one Board | Not explicitly specified | Present in create request. A Task belongs to one Board. |
| `title` | Model data | Task | Not explicitly specified | Appears in create/update requests. |
| `description` | Model data | Task | Not explicitly specified | Appears in create/update requests. |
| `status` | Model data | Task | Not explicitly specified | Must use one of the documented allowed values. |
| `priority` | Model data | Task | Not explicitly specified | Must use one of the documented allowed values. |
| `assignee` | Relationship | Zero or one User | Optional | If set, the User must be a member of the same Board. |
| `reviewer` | Relationship | Zero or one User | Optional | If set, the User must be a member of the same Board. |
| `due_date` | Model data | Task | Not explicitly specified | Appears in create/update requests. |
| `comments_count` | Calculated | From related Comments | API-calculated | Number of Comments attached to the Task. |
| `creator` | Relationship | Exactly one User | Required by business rule; exact API field name not specified | Needed because only the Task creator or Board owner may delete the Task. |

### Allowed Task Values

| Field | Allowed Values |
|---|---|
| `status` | `to-do`, `in-progress`, `review`, `done` |
| `priority` | `low`, `medium`, `high` |

### Task Business Rules

| Rule | Requirement |
|---|---|
| Task → Board | A Task belongs to exactly one Board. |
| Board → Tasks | A Board can contain multiple Tasks. |
| Create Task | Requesting user must be an authenticated member of the Board. |
| Update Task | Requesting user must be an authenticated member of the Board. |
| Change Task Board | Not allowed after Task creation. |
| Assignee | Optional; zero or one User; must belong to the same Board. |
| Reviewer | Optional; zero or one User; must belong to the same Board. |
| Delete Task | Only the Task creator or the Board owner may delete it. |
| Partial update | Fields that should not change may be omitted from the PATCH request. |

---

## 4. Comment Requirements

### Comment Data and Relationships

| Item | Classification | Cardinality / Source | Required / Optional | Notes |
|---|---|---|---|---|
| `id` | Model data | System-generated | System-generated | Comment identifier. |
| `content` | Model data | Comment | Present in create request; empty content is invalid | Main Comment text. |
| `created_at` | Model data | Generated automatically | System-generated | Creation timestamp returned by the API. |
| `task` | Relationship | Exactly one Task | Implied by endpoint structure | Every Comment belongs to one specific Task. |
| `author` | Relationship | Exactly one User | Assigned automatically | Derived from the authenticated user; client does not send it. |

### Comment Business Rules

| Rule | Requirement |
|---|---|
| Task → Comments | One Task can have multiple Comments. |
| Comment → Task | Each Comment belongs to exactly one Task. |
| Author assignment | The authenticated user becomes the Comment author automatically. |
| Create Comment | User must be an authenticated member of the Task's Board. |
| Read Comments | User must be an authenticated member of the Task's Board. |
| Delete Comment | Only the Comment author may delete it. |
| Empty content | Invalid and may produce `400 Bad Request`. |
| Ordering | Comments are returned in chronological order by creation time. |
| Missing Task/Comment | Documented delete behavior returns `404` if the Task or Comment does not exist. |

---

## 5. Relationship Overview

| From | Relationship | To | Cardinality / Rule |
|---|---|---|---|
| `Board` | `owner` | `User` | Exactly one owner per Board. |
| `Board` | `members` | `User` | Multiple Users per Board. Owner may also be a member. |
| `Board` | `tasks` | `Task` | One Board can have multiple Tasks. |
| `Task` | `board` | `Board` | Exactly one Board per Task. |
| `Task` | `assignee` | `User` | Zero or one User; must be a Board member. |
| `Task` | `reviewer` | `User` | Zero or one User; must be a Board member. |
| `Task` | `creator` | `User` | Exactly one creator is required by deletion rules; exact model field name is not specified. |
| `Task` | `comments` | `Comment` | One Task can have multiple Comments. |
| `Comment` | `task` | `Task` | Exactly one Task per Comment. |
| `Comment` | `author` | `User` | Exactly one User; assigned from authentication. |

---

## 6. Values That Should Not Become Independent Stored Model Fields

These values appear in API responses but can be derived from other data:

| API Value | Derived From |
|---|---|
| `member_count` | Number of Board members |
| `ticket_count` | Number of Tasks on the Board |
| `tasks_to_do_count` | Tasks with `status = "to-do"` |
| `tasks_high_prio_count` | Tasks with `priority = "high"` |
| `comments_count` | Number of Comments on the Task |
| `owner_id` / `owner_data` | Different representations of the Board owner relationship |
| `members` / `members_data` | Different representations of the Board members relationship |

---

## 7. Documentation Gaps / Important Non-Assumptions

The API documentation does **not** explicitly state requiredness for several fields. Do not silently convert example request bodies into required-field rules.

| Field | Documentation Status |
|---|---|
| `Board.title` | Appears in requests; requiredness not explicitly stated. |
| `Board.members` | Appears in requests; requiredness not explicitly stated. |
| `Task.board` | Present in create request and conceptually required for Board membership rules; requiredness is not explicitly stated. |
| `Task.title` | Appears in requests; requiredness not explicitly stated. |
| `Task.description` | Requiredness not explicitly stated. |
| `Task.status` | Requiredness not explicitly stated; allowed values are explicitly defined. |
| `Task.priority` | Requiredness not explicitly stated; allowed values are explicitly defined. |
| `Task.due_date` | Requiredness not explicitly stated. |
| `Task.creator` | Needed by the documented delete rule, but the exact model field name is not specified. |

Explicitly documented optional fields:

- `Task.assignee`
- `Task.reviewer`

---

## 8. Card 06 Result

The model-design requirements derived from the complete API documentation are now clear enough to continue to the actual Django model design step.

Before implementation, the model design must preserve these key facts:

1. A Board has one owner, multiple members, and multiple Tasks.
2. A Task belongs to one Board.
3. A Task may have zero or one assignee and zero or one reviewer.
4. Assignee and reviewer must belong to the Task's Board.
5. The Task's Board cannot be changed after creation.
6. Task deletion requires knowledge of the Task creator.
7. A Comment belongs to one Task and one author.
8. Comment author is determined automatically from authentication.
9. Deleting a Board removes related Tasks and Comments.
10. Count fields shown by the API are calculated values, not independent domain data.

---

## Source Reference

Derived from:

- Official **KanMind API Endpoint Dokumentation**
- **KanMind Backend Master Checklist**
- Trello Card **[06] Model-Anforderungen aus kompletter API-Doku ableiten**

No Django model implementation is included in this document.
