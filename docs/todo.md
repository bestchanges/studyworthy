##### [Content](CONTENT.md)
- [x] admin: view course (codes, sections, units)
- [x] unit order is course-wide. Not in section
- [ ] redo import as django command accepting course.yaml
##### [Learnings](LEARNINGS.md)
- [x] create command for scheduled jobs
- [x] start course and open lesson automatically
- [x] Lesson on save() trigger appropriate django signals to apps
##### [Domain Model](MODELS.md)
##### Student enrollment
- [ ] student application form (exportable to external sites)
- [ ] assign student as candidate to learning/course(?)
- [ ] application notification to course manager(!)
- [ ] update payment and participant status  
- [ ] list payment status for admin
- [ ] Send welcome message to Student onActivate() 
##### Student UI
- [ ] my courses
- [ ] view course
- [ ] timezone aware views
- [ ] view unit
    - [ ] md plugin for template expansion (1h)
##### [REST API](API.md)
- [ ] search participant by repository
- [ ] search unit by path
- [ ] provide python client lib
##### Slack integration
- [x] slack integration spike (3h)
- [ ] invite users to account (using invite link in )
##### [CLI client library](CLI.md)
