##### [Root app](ROOTAPP.md)
- [ ] EnrollmentForm make logged-in (use two different forms / hide some fields)
- [ ] Enrollment Form map to existing / creating new Person
    - [ ] use lookup Person for authorization dashboard (and rename it from dashboard to after-auth0-auth)
##### [Campus APP](CAMPUS.md)
##### [LMS](LMS.md)
- [ ] spike for forms / quizzes
  - [x] model: Form(Content) (slug, name, type: quiz/poll)
  - [x] model: Question (code, name, hint, type, values, correct_values, score)
  - [ ] admin: Form with inline questions
  - [ ] views: render Form
  - [ ] views: response = form.get_response(request)
  - [ ] views: form.render_response(response)
  - [x] investigate https://github.com/stephenmcd/django-forms-builder,
       https://github.com/tomwalker/django_quiz
- [ ] rename Decision to StudentResponse
- [ ] rename Review to TeacherFeedback
- [ ] mapping from content type to proxy model (no need to model inheritance)
  - [ ] extract ContentType to separate class (remove Content/Type)
  - [ ] proxy models for Content types
  - [ ] method render
- [ ] support for webinar/youtube as content-type
  - [ ] render player
   https://developers.google.com/youtube/youtube_player_demo
  - [ ] render chat
- [ ] CHALLENGE! How to share materials between different courses???
  - [ ] model Unit has many-to-many relations with Content
  - [ ] update importer to use UnitContent
- [ ] importer: fix bug. Only one content item is added to the course
- [ ] importer: clean units items not in file but in DB
  - [ ] importer: use field delete to delete units, sections
##### [CRM](CRM.md)
##### Notification app
- [ ] 'notifications' application in Django
- [ ] skackbot dependency
##### [Architecture](ARCH.md)
- [ ] Webinar is a specific case of Course (with Content webinar)
##### [Systems](SYSTEMS.md)
- [ ] use django-debug-toolbar (only on dev)
##### [Design](DESIGN.md)
