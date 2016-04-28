from django.views.generic.edit import FormView
from django.views.generic import CreateView
from django.shortcuts import force_text
import datetime, re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class FormNextView(FormView):
    def get_context_data(self, **kwargs):
        context = super(FormNextView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))


class CreateNextView(CreateView):
    def get_context_data(self, **kwargs):
        context = super(CreateNextView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))


class UpdateNextView(CreateView):
    def get_context_data(self, **kwargs):
        context = super(UpdateNextView, self).get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', self.request.POST.get('next', self.success_url))
        return context

    def get_success_url(self):
        return force_text(self.request.GET.get('next', self.request.POST.get('next', self.success_url)))


class ListCompleteView(FormView):
    """
    A faire par l'utilisateur de cette classe:
    renseigner form_class, template_name, success_url, attr (avec les valeurs initiales)
    get_form_kwargs
    form_valid -> mettre à jour les valeurs dans attr en fonction des réponses
    """
    form_class = None
    template_name = None
    success_url = None
    attr = {}
    query = None
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        # Récupération des paramètres GET

        # Gestion des dates
        pattern_date = re.compile('[0-9]{2}-[0-9]{2}-[0-9]{4}')

        for name in self.attr.keys():
            if request.GET.get(name) is not None:
                # Cas des bools
                if request.GET.get(name) == 'False':
                    self.attr[name] = False
                elif request.GET.get(name) == 'True':
                    self.attr[name] = True
                # Cas des dates
                elif pattern_date.match(request.GET.get(name)) is not None:
                    split_date = request.GET.get(name).split('-')
                    self.attr[name] = datetime.date(int(split_date[2]), int(split_date[1]), int(split_date[0]))
                # Autres
                else:
                    self.attr[name] = request.GET.get(name)

        return super(ListCompleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        # Récupération des paramètres POST
        for name in self.attr.keys():
            if request.POST.get(name) is not None:
                # Cas des bools
                if request.POST.get(name) == 'False':
                    self.attr[name] = False
                elif request.POST.get(name) == 'True':
                    self.attr[name] = True
                # Autres
                else:
                    self.attr[name] = request.POST.get(name)
        return super(ListCompleteView, self).post(request, *args, **kwargs)

    def get_initial(self):
        initial = super(ListCompleteView, self).get_initial()
        for name in self.attr.keys():
            initial[name] = self.attr[name]
        return initial

    def get_context_data(self, **kwargs):
        context = super(ListCompleteView, self).get_context_data(**kwargs)
        for name in self.attr.keys():
            if isinstance(self.attr[name], datetime.date):
                context[name] = self.attr[name].strftime('%d-%m-%Y')
            else:
                context[name] = self.attr[name]

        # Pagination
        notifications_list_paginator = Paginator(self.query, self.paginate_by, orphans=0,
                                                 allow_empty_first_page=True)
        context['paginator'] = notifications_list_paginator
        # Filtre de la page à afficher en fonction de la requête
        page = self.request.GET.get('page')
        if page == 'last':
            # If page is 'last', deliver first page.
            page = notifications_list_paginator.num_pages
        elif page == 'first':
            # If page is 'first', deliver first first.
            page = 1
        try:
            notifications_list_page = notifications_list_paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = 1
            notifications_list_page = notifications_list_paginator.page(page)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = notifications_list_paginator.num_pages
            notifications_list_page = notifications_list_paginator.page(page)
        context['page'] = notifications_list_page

        page_links = []
        for page_number in notifications_list_paginator.page_range:
            if (int(page) - 1) <= page_number <= (int(page) + 1):
                page_links.append(page_number)
        context['page_links'] = page_links
        return context

