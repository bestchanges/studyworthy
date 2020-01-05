# Backlog Tasks
- [ ] importer: clean content items not in file but in DB (content-always)
- [ ] admin: course content modification
- [ ] admin: Unit with Content Inline
- [ ] redo import as django command accepting course.yaml


# Solution
- unit content = single .md file
- all media files are external (possible other solution by plugin)
- clone learning

# IDEAS
- Separate unit's tasks from study content<br>

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

# References
* https://neutronx.github.io/django-markdownx/
* https://github.com/agusmakmun/django-markdown-editor
