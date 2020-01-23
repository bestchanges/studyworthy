##### [Root app](ROOTAPP.md)
- [ ] EnrollmentForm make logged-aware (actually use two different forms)
- [ ] Enrollment Form map to existing / creating new Person
    - [ ] use lookup Person for authorization dashboard (and rename it from dashboard to after-auth0-auth)
- [ ] Enrollment also Invoice
##### [Campus APP](CAMPUS.md)
##### [LMS](LMS.md)
- [ ] model Unit has many-to-many relations with Content
    - [x] model Unit display content inline according to order
    - [x] can create new Content from Unit edit
    - [x] can go to unit from Course edit
    - [x] fix fixtures
    - [ ] update importer to use UnitContent
- [x] models in learning.py inherit NaturalKeyModel
- [x] make Unit order field not unique with!
- [x] make Units to order by order in admin
- [x] admin Course: authors should autocompletion by name
##### [CRM](CRM.md)
##### [REST API](API.md)
##### Notification app
- [ ] 'notifications' application in Django
- [ ] skackbot dependency
##### [CLI client library](CLI.md)
##### [Architecture](ARCH.md)
- [ ] Model's code generator
    - [x] Let's use this: https://github.com/wq/django-natural-keys
    - [x] auto generate code (uuid, or dependant on properties with prefix/suffix)
    - [ ] add L to learnings code
##### [Systems](SYSTEMS.md)
##### [Design](DESIGN.md)
