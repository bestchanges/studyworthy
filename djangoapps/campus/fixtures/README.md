# Fixture for testing

## Courses:
```python
 Course(title='Course Number 1', code='course-1', state='active')
 Course(title='Course Number 2', code='course-2', state='active')
 Course(title='Course Number 3', code='course-3', state='archived')
```
* Each course has 15-25 units
## Learnings
```python
 Learning(course='Course Number 1', code='course-1-L1', state='planned')
 Learning(course='Course Number 1', code='course-1-L2', state='ongoing')
 Learning(course='Course Number 2', code='course-2-L1', state='planned')
```
### Participants
* dasha@email.com - has 2 courses
* dima@email.com - has 1 course
