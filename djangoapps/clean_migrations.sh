for app in siteroot erp crm lms lms_cms yandex_kassa ; do
  rm ${app}/migrations/*.py
  touch ${app}/migrations/__init__.py
done

rm ../db-tests.sqlite3

(
cd ..
pipenv run python manage.py makemigrations
)