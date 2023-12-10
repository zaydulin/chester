from random import randrange

from django.db import models
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.utils.text import slugify
from _project import settings


class Rubrics(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.DateTimeField(auto_now=True)
    name = models.CharField("Название", max_length=500, null=True)
    description = models.TextField("Описание",null=True)
    title = models.CharField("Заголовок", max_length=500, null=True)
    api_id = models.PositiveIntegerField("ID спорта", null=True)
    content = models.TextField("Мета-описание", max_length=500, null=True)
    slug = models.SlugField("Ссылка", max_length=160, unique=True)
    icon = models.ImageField("Иконка цветная",default="default/generals/no-image.jpg", blank=True, null=True)
    icon2 = models.ImageField("Иконка черная",default="default/generals/no-image.jpg", blank=True, null=True)
    cover = models.ImageField("Обложка",default="default/generals/no-image.jpg", blank=True, null=True)
    sortable = models.PositiveIntegerField("Сортивароть", unique=True, null=True)
    second_api = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('rubric', kwargs={"slug": self.slug})
    def __str__(self):
        return f'{self.name} - {self.slug}'
    class Meta:
        verbose_name = 'Рубрики'
        verbose_name_plural = 'Рубрики'

class Events(models.Model):
    STATUS = [
        (1, 'Прямой эфир'),
        (2, 'Завершенные'),
        (3, 'Предстоящие'),
        (4, 'Отменён'),
    ]
    rubrics = models.ForeignKey(Rubrics, verbose_name='Рубрики', on_delete=models.CASCADE, related_name="events")
    id = models.AutoField(primary_key=True)
    event_api_id = models.PositiveIntegerField("ID API",blank=True,null=True)
    second_event_api_id = models.CharField("ID API 2 ",max_length=150,blank=True,null=True)
    data = models.DateTimeField(auto_now=True)
    start_at = models.DateTimeField('Начало', null=True)
    name = models.CharField("Название", max_length=500, null=True)
    description = models.TextField("Описание",null=True)
    title = models.CharField("Заголовок", max_length=500, null=True)
    content = models.TextField("Мета-описание", max_length=500, null=True)
    slug = models.SlugField("Ссылка", max_length=160,blank=True)
    status = models.PositiveSmallIntegerField('Статус', choices=STATUS, default=3)
    home_team = models.ForeignKey("Team", verbose_name='Домашняя комнада', on_delete=models.CASCADE,related_name="home_team",blank=True,null=True)
    away_team = models.ForeignKey("Team", verbose_name='Гостевая комнада', on_delete=models.CASCADE,related_name="away_team",blank=True,null=True)
    home_score = models.PositiveIntegerField("Очки дома",default=0,blank=True,null=True)
    periods = models.ManyToManyField("Periods",verbose_name='Половина',blank=True)
    away_score = models.PositiveIntegerField("Очки гостей",default=0,blank=True,null=True)
    half = models.CharField("Половина",max_length=150,blank=True,null=True)
    reschedule = models.BooleanField('Событие перенесено по времени',default=False)
    section = models.ForeignKey("Season",verbose_name='Сезон',on_delete=models.CASCADE,blank=True,null=True)
    incidents = models.ManyToManyField("Incidents",verbose_name='События(голы и тд)',blank=True)
    statistic = models.ManyToManyField("GameStatistic",verbose_name='Статистика за матч',blank=True)
    tennis_points = models.ManyToManyField("TennisPoints",verbose_name='Теннисные очки',blank=True)
    h2h = models.ManyToManyField("H2H", verbose_name='H2H', blank=True)

    def get_absolute_url(self):
        return reverse('events', kwargs={"slug": self.slug})

    def get_correct_half(self):
        if self.half:
            if self.half == '1st half':
                return '1 тайм'
            if self.half == '2st half':
                return '2 тайм'
            if self.half == 'Halftime':
                return 'Перерыв'
            if self.half == 'FT':
                return 'Матч закончен'
            else:
                return 'Матч не начался'

    def save(self, *args, **kwargs):
        original_slug = f'{self.home_team}-{self.away_team}-{self.start_at}'
        if not Events.objects.filter(slug=original_slug):
            # Создаем slug из полей home_team, away_team и start_at
            slug_text = f'{self.home_team}+{self.away_team}+{self.start_at}'

            # Заменяем пробелы на тире
            slug_text = slug_text.replace(' ', '-')

            # Словарь для замены русских букв на английские
            translit_dict = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
                'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
            }

            # Преобразуем текст, заменяя русские буквы на английские
            slug_text = ''.join(translit_dict.get(c.lower(), c) for c in slug_text)

            # Преобразуем текст в slug
            self.slug = f'smotret-online-{slugify(slug_text)}'

        super(Events, self).save(*args, **kwargs)

    def get_start_time(self):
        if self.start_at:
            # Convert the DateTime to the local timezone if necessary
            local_start_time = timezone.localtime(self.start_at)
            return local_start_time.strftime('%H:%M')
        return None

    def get_start_date(self):
        if self.start_at:
            # Convert the DateTime to the local timezone if necessary
            local_start_time = timezone.localtime(self.start_at)
            return local_start_time.strftime('%Y-%m-%d')
        return None

    def __str__(self):
        status_str = next((status[1] for status in self.STATUS if status[0] == self.status), "Unknown")
        return f'{self.section} - {self.name} - {status_str} - {self.start_at} - {self.rubrics.name}'

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class TennisPoints(models.Model):
    api_id_tp =  models.CharField('ID API ',max_length=150)
    set = models.CharField('Сэт',max_length=150)
    games = models.ManyToManyField('TennisGames',verbose_name='Теннисные игры',blank=True )

    class Meta:
        verbose_name = 'Теннисные очки'
        verbose_name_plural = 'Теннисные очки'

class TennisGames(models.Model):
    game = models.CharField('Игра',max_length=150)
    home_score = models.CharField('Очки дома',max_length=150)
    away_score = models.CharField('Очки гостей',max_length=150)
    points = models.ManyToManyField('Points',verbose_name='Очки',blank=True)
    serving = models.CharField('Подача',max_length=15)
    class Meta:
        verbose_name = 'Теннисные игры'
        verbose_name_plural = 'Теннисные игры'

class Points(models.Model):
    homePoint = models.CharField('Очки дома',max_length=150)
    awayPoint = models.CharField('Очки гостей',max_length=150)
    class Meta:
        verbose_name = 'Теннисные поинты'
        verbose_name_plural = 'Теннисные поинты'

class H2H(models.Model):
    home_score =models.PositiveIntegerField("Очки дома",default=0,blank=True,null=True)
    away_score =models.PositiveIntegerField("Очки гостей",default=0,blank=True,null=True)
    api_h2h_id = models.PositiveIntegerField("ID API",blank=True,null=True)
    name = models.CharField("Название", max_length=500, null=True)
    home_team_ID = models.PositiveIntegerField("ID Дома ",default=0,blank=True,null=True)
    away_team_ID = models.PositiveIntegerField("ID Гостей",default=0,blank=True,null=True)
    home_team_NAME = models.CharField("NAME Дома", max_length=500,blank=True,null=True)
    home_team_LOGO = models.ImageField("home_team_LOGO",default="default/generals/no-image.jpg", blank=True, null=True)
    away_team_NAME = models.CharField("NAME Гостей", max_length=500,blank=True,null=True)
    away_team_LOGO = models.ImageField("away_team_LOGO",default="default/generals/no-image.jpg", blank=True, null=True)
    league = models.CharField("Название", max_length=500, null=True)
    league_logo = models.ImageField("Изображения",default="default/generals/no-image.jpg", blank=True, null=True)
    start_at = models.DateTimeField('Начало', null=True)
    h_result = models.CharField("H_RESULT", max_length=500, blank=True, null=True)
    team_mark = models.CharField("TEAM_MARK", max_length=500, blank=True, null=True)

    def __str__(self):
        return f'{self.home_team_NAME}-{self.away_team_NAME}'

    class Meta:
        verbose_name = 'H2H'
        verbose_name_plural = 'H2H'

class Periods(models.Model):
    event_api_id =models.PositiveIntegerField("ID API")
    home_score = models.IntegerField("Очки дома")
    away_score = models.IntegerField("Очки гостей")
    period_number = models.PositiveIntegerField("Номер периода")

    def __str__(self):
        return f'{self.event_api_id} - Dom - {self.home_score} - Guests - {self.away_score} - Period - {self.period_number}'

    class Meta:
        verbose_name = 'Период'
        verbose_name_plural = 'Периоды'


class Team(models.Model):
    rubrics = models.ForeignKey(Rubrics, verbose_name='Рубрики', on_delete=models.CASCADE)
    name = models.CharField("Название", max_length=500, null=True)
    slug = models.SlugField("Ссылка", max_length=160, unique=True,blank=True)
    api_team_id = models.PositiveIntegerField("ID команды",null=True)
    second_api_team_id = models.CharField("ID команды",max_length=150,null=True)
    description = models.TextField("Описание",null=True)
    logo = models.ImageField("Изображения",default="default/generals/no-image.jpg", blank=True, null=True)
    players = models.ManyToManyField('Player',verbose_name="Игроки")


    def save(self, *args, **kwargs):
        loop_num = 0
        unique = False
        while not self.slug and not unique:
            if loop_num < settings.RANDOM_URL_MAX_TRIES:
                new_key = ''
                for i in range(settings.RANDOM_URL_LENGTH):
                    new_key += settings.RANDOM_URL_CHARSET[
                        randrange(0, len(settings.RANDOM_URL_CHARSET))]
                if not Team.objects.filter(slug=new_key):
                    self.slug = new_key
                    unique = True
                loop_num += 1
            else:
                raise ValueError("Couldn't generate a unique code.")

        super(Team, self).save(*args, **kwargs)
    def __str__(self):
        return f'{self.name} - {self.api_team_id}'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Season(models.Model):
    rubrics = models.ForeignKey(Rubrics, verbose_name='Рубрики', on_delete=models.CASCADE)
    season_name = models.CharField("Название сезона", max_length=500, null=True)
    league_name = models.CharField("Название лиги", max_length=500, null=True)
    slug = models.SlugField("Ссылка", max_length=160, unique=True,blank=True)
    league_id = models.CharField("ID лиги", max_length=500,null=True)
    season_id = models.CharField("ID сезона", max_length=500,null=True)
    season_second_api_id = models.CharField("API ID 2", max_length=500, null=True)
    logo_league = models.ImageField("Изображения",default="default/generals/no-image.jpg", blank=True, null=True)
    description = models.TextField("Описание", null=True)
    popular = models.BooleanField(default=False)
    country = models.ForeignKey("Country", on_delete=models.CASCADE,blank=True, null=True)
    def __str__(self):
        return f'{self.league_name} - {self.season_name}'

    def save(self, *args, **kwargs):
        loop_num = 0
        unique = False
        while not self.slug and not unique:
            if loop_num < settings.RANDOM_URL_MAX_TRIES:
                new_key = ''
                for i in range(settings.RANDOM_URL_LENGTH):
                    new_key += settings.RANDOM_URL_CHARSET[
                        randrange(0, len(settings.RANDOM_URL_CHARSET))]
                if not Season.objects.filter(slug=new_key):
                    self.slug = new_key
                    unique = True
                loop_num += 1
            else:
                raise ValueError("Couldn't generate a unique code.")
        super(Season, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Лига'
        verbose_name_plural = 'Лиги'

class Country(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField('Флаг',default='default/russia_flag.jpg')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

class PopularSeasons(models.Model):
    season = models.ForeignKey(Season,verbose_name="Лига",on_delete=models.CASCADE)
    position = models.PositiveIntegerField('Позиция в списке ')

    def __str__(self):
        return f'Position - {self.position} , League - {self.season},'


    class Meta:
        verbose_name = 'Популярная Лига'
        verbose_name_plural = 'Популярные Лиги'

class Incidents(models.Model):
    rubrics = models.ForeignKey(Rubrics, verbose_name='Рубрики', on_delete=models.CASCADE)
    incident_type = models.CharField("Тип", max_length=500, null=True)
    player = models.ForeignKey('Player',on_delete=models.CASCADE,verbose_name="Игрок",blank=True,null=True,related_name='incidents_player')
    player_two_in = models.ForeignKey('Player',on_delete=models.CASCADE,verbose_name="Игрок",blank=True,null=True,related_name='incidents_player_two_in')
    player_team = models.PositiveIntegerField('Событие команды',null=True)
    description = models.TextField("Описание", null=True)
    card_type = models.CharField("Цвет карточки",max_length=150,blank=True)
    time = models.CharField("Время события",max_length=150,blank=True)
    inj_time = models.CharField("Доп время",max_length=150,blank=True)
    scoring_team = models.CharField("Команда забившая",max_length=150,blank=True)

    def __str__(self):
        return f'{self.incident_type} - {self.player}'

    class Meta:
        verbose_name = 'Событие(голы и тд)'
        verbose_name_plural = 'События(голы и тд)'

class GameStatistic(models.Model):
    period = models.CharField('Период', max_length=500)
    name = models.CharField("Название статистики", max_length=500, null=True)
    home = models.CharField("Кол-во у дома",max_length=150)
    away = models.CharField("Кол-во у гостей",max_length=150)
    description = models.TextField("Описание", null=True)

    def __str__(self):
        return f'Период -{self.period} -Название  {self.name}'

    class Meta:
        verbose_name = "Игровая статистика"
        verbose_name_plural = "Игровые статистики"


class Player(models.Model):
    player_id = models.PositiveIntegerField('ID игрока API',null=True)
    slug = models.SlugField("Ссылка", max_length=160, unique=True)
    name = models.CharField("Имя игрока", max_length=500, null=True)
    photo = models.ImageField("Изображения",default="default/generals/no-image.jpg", blank=True, null=True)
    position_name = models.CharField("Позиция", max_length=500, null=True)
    description = models.TextField("Описание", null=True)
    main_player = models.BooleanField('Состояние замены', default=False)
    reiting = models.CharField("Рейтинг", max_length=500, null=True)
    number = models.CharField("Номер", max_length=500, null=True)

    def __str__(self):
        return f'{self.name} - {self.player_id}'

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'


