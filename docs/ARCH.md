## Backlog
- [ ] extract created_at, updated_at as Mixin (what to do with readonly fields?)
- [ ] use of https://docs.djangoproject.com/en/3.0/ref/contrib/humanize/

## IDEAs
- [ ] stop redefining AuthUser. We can match it to person on fly. And keep it in session by the way on signal login.

## Проблема с именем пользователя.
Если человек приходит с Auth0 с формы регистрации,
то у него нет имени и фамилии.
- [x] Можно исопльзовать имя из емэйла до собаки
- [ ] Можно запросить после
- [ ] Можно отказаться от сериса
- [ ] Можно ничего не делать

## Applications
- Core 
- Admin (Teacher)
- CRM
- Study Student?
- Promo
- Slack
