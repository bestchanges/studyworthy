# LMS App

# Backlog Tasks
- [ ] make Lessons to order by order
- [ ] admin Content add: list_fields, search_fields
- [ ] model Content introduce 'data' JSONFiled
  solution for sqlite: https://medium.com/@philamersune/using-postgresql-jsonfield-in-sqlite-95ad4ad2e5f1
- [ ] importer: fix bug. Only one content item is added to the course
- [ ] importer: clean content items not in file but in DB (content-always)
- [ ] Learning schedule inherits from course.default_schedule 
- [ ] Content: import partly from markdown (2h)
- [ ] Learning clone (as draft, keep teacher, admin) 
- [ ] make section field limit_choises_to 
    sample solution: https://stackoverflow.com/questions/31578559/django-foreignkey-limit-choices-to-a-different-foreignkey-id


# IDEAS / Issues
- [ ] store course content with mediafiles in this repo. Thus we can easily deliver media files

# Solution

# Check Requirements
- [x]  Удобство создания и визуального обзора материалов
- (?)  Удобство навигации между документами
- -nope-  Версии, бранчи
- [x]  Удобство редактирования. Ничего лишнего, концентрация на контенте
- [x]  Лёгкость преобразования в HTML с прекрасными визуальными возможностями
- [x]  Дать возможность удобно смотреть видео на любом устройстве (Ютуб!)
- [x]  Хостинг медиа файлов. Разные варианты. 
    - Все медиа хранить в отдельных сервисах и встраивать в контент по ссылке. YouTube, S3. 
    - Данные для проектов распространять через проектный репозиторий. 
    - Бесплатный. На гитхаб. Только картинки и прочие мелочи. Проверить можно ли на них ссылаться из стороннего сайта
    - Хостить в Джанго на хостинге.
- (?) Делать разметку: задание, важное замечание, программный код
- (?)  Возможность Использовать Jupyter, repl.io
- [x]  Возможность смотреть контент через слак (и текст и видео)

# LMS Resuirments

- [x]  Добавлять студентов и преподавателей на платформу
- [x]  Назначать студентов на группу по курсу
- [x]  Назначать учителя и эксперта' на группу
- [ ]  Отправить уведомление студентам одной группы о живом вебинаре
- [ ]  Отправить учебные материалы урока - видео, документ, презентация
- [ ]  Принять от студента результат задания и передать его учителю
- [ ]  Принять ответ студента и проверить его автоматически
- [ ]  Поставить отметку о посещении урока учеником
- [ ]  Принять отметку учителя на результат задания
- [ ]  Показать успеваемость студента
- [ ]  Напомнить студенту о пропущенных уроках
