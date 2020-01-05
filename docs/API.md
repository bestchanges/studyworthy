# TASKS
- [ ] search participant by repository
- [ ] search unit by path
- [ ] provide python client lib
- [ ] secure POST submission endpoint to only teachers of this Learning
- [ ] add checkmark as units/{}/checkmark
- [ ] secure PIT/DELETE operations
- [ ] GET /units/ take learning param in consideration
- [ ] make API refer to code instead of ID


## add submission
* POST /submissions/create ?
    * unit unit.code
    * student student-code
* fields: 
* Who can: student/bot

## add submission
* POST /submissions/result ?unit=unit-code&student=student-code
* Who can: student/bot
