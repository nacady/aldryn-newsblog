from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.http import HttpResponse
from aldryn_apphooks_config.mixins import AppConfigMixin

from .models import Article


class ArticleDetail(AppConfigMixin, DetailView):
    def get_queryset(self):
        return Article.objects.filter(namespace__namespace=self.namespace)


class ArticleList(AppConfigMixin, ListView):
    @property
    def queryset(self):
        return Article.objects.filter(namespace__namespace=self.namespace)

    def get(self, request):
        return HttpResponse('\n'.join(
            article.title for article in self.queryset))


class AuthorArticleList(ArticleList):
    """A list of articles written by a specific author."""
    @property
    def queryset(self):
        return super(AuthorArticleList, self).queryset.filter(
            author__slug=self.author)

    def get(self, request, author):
        self.author = author
        return super(AuthorArticleList, self).get(request)


class CategoryArticleList(ArticleList):
    """A list of articles filtered by categories."""
    @property
    def queryset(self):
        return super(CategoryArticleList, self).queryset.filter(
            categories__translations__slug=self.category
        )

    def get(self, request, category):
        self.category = category
        return super(CategoryArticleList, self).get(request)


class DateRangeArticleList(ArticleList):
    """A list of articles for a specific date range"""
    @property
    def queryset(self):
        return super(DateRangeArticleList, self).queryset.filter(
            publishing_date__gte=self.date_from,
            publishing_date__lt=self.date_to)

    def _daterange_from_kwargs(self, kwargs):
        raise NotImplemented('Subclasses of DateRangeArticleList need to'
                             'implement `_daterange_from_kwargs`.')

    def get(self, request, **kwargs):
        self.date_from, self.date_to = self._daterange_from_kwargs(kwargs)
        return super(DateRangeArticleList, self).get(request)


class YearArticleList(DateRangeArticleList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), 1, 1)
        date_to = date_from + relativedelta(years=1)
        return date_from, date_to


class MonthArticleList(DateRangeArticleList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(int(kwargs['year']), int(kwargs['month']), 1)
        date_to = date_from + relativedelta(months=1)
        return date_from, date_to


class DayArticleList(DateRangeArticleList):
    def _daterange_from_kwargs(self, kwargs):
        date_from = datetime(
            int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        date_to = date_from + relativedelta(days=1)
        return date_from, date_to
