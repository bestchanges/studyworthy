Build:
 [![Travis](https://travis-ci.org/bestchanges/studyworthy.svg?branch=master)](https://travis-ci.org/bestchanges/studyworthy)
 [![Coverage Status](https://coveralls.io/repos/github/bestchanges/studyworthy/badge.svg?branch=master)](https://coveralls.io/github/bestchanges/studyworthy?branch=master)
# References

* [Canban board](https://github.com/bestchanges/studyworthy/projects/1)
* [Unassigned Issues](https://github.com/bestchanges/studyworthy/issues?q=is%3Aopen+is%3Aissue+no%3Aassignee)
* [Wiki](https://github.com/bestchanges/studyworthy/wiki)

### How to start
```
pip install -r requirements.txt

pip install pipenv

pipenv install

python manage.py migrate

# seed db with initial data
python manage.py loaddata initial_data

python manage.py runserver

./manage.py test
```

## Sessions
* [StudyWorthy project presentation ](https://youtu.be/Fq3F8vt_PcI)
* [StudyWorthy project update 27.06](https://youtu.be/zDgZCDqagTA)
