from django.shortcuts import render
from .forms import SearchForm
#from .query_sphinx import QuerySphinx
from .models import HistoryRecords
from users.models import IP
from django.http import HttpResponseRedirect
from django.urls import reverse
# from dal import autocomplete
from math import ceil
from query_sphinx.make_connections import MakeConnections
# from query_sphinx.query_sphinx_test import QuerySphinx
from query_sphinx.query_sphinx import QuerySphinx
from ipware import get_client_ip
from datetime import timedelta
from django.utils import timezone
import re

sphinx_client, mydb, mydbcursor = MakeConnections()
language_code = {"en":"English", "ru":"Russian", "fr":"French"}
blank_search_form = {'query':'', 'lang1':"en", 'lang2':"ru",
    'res_per_page':25, 'pos_tags':False}

#detects user's ip, adds new ip to the database, renews quota for old ip if necessary
def check_ip(request):
    client_ip, is_routable = get_client_ip(request)
    ip = IP.objects.filter(ip=client_ip)
    if not ip:
        new_ip = IP.objects.create(ip = client_ip)
        return new_ip
    else:
        old_ip = ip[0]
        # today = date.today().strftime("%Y-%m-%d")
        last_connection = old_ip.last_connection
        # start_time = timezone.make_aware(datetime.now()-timedelta(days=1), timezone.get_default_timezone())
        #last_connection = str(last_connection)
        # if today!=last_connection:
        # if old_ip.last_connection <= start_time:
        #if previous query quota was set more than 24 hours ago, renew the quota
        if last_connection <= timezone.now() - timedelta(days=1):
                old_ip.n_requests = 50
                old_ip.last_connection =  timezone.now()
                old_ip.last_query = ''
                old_ip.save()
        return old_ip

class Paginator():
    def __init__(self, has_other_pages = 0,
    has_previous = 0, previous_page_number = None, page_range = list(),
    number = 0, has_next = 0, next_page_number = 0 ):
        self.has_other_pages = has_other_pages
        self.has_previous = has_previous
        self.previous_page_number = previous_page_number
        self.page_range = page_range
        self.number = number
        self.has_next = has_next
        self.next_page_number = next_page_number

#home page
#for the POST request redirect to the search view, render the default form otherwise
def index(request):

    form = SearchForm(initial=blank_search_form)

    if request.method=='POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            query = cd.get('query')
            lang1 = cd.get('lang1')
            lang2 = cd.get('lang2')
            # sci_mode = cd.get('sci_mode')
            res_per_page = cd.get('res_per_page')
            pos_tags = cd.get('pos_tags')
            #add the query to user's history
            if request.user.is_authenticated:
                new_record = HistoryRecords(query=query, owner_id=request.user.id)
                new_record.save()
                all_records = HistoryRecords.objects.filter(owner=request.user).order_by('date_added')
                if len(all_records)>30:
                    all_records[0].delete()
            return HttpResponseRedirect('/search/?q={}&lang1={}&lang2={}&num={}&pos_tags={}'.format(query, lang1, lang2, res_per_page, pos_tags))

    context = {'form': form, 'excerpts': None}
    return render(request, 'wordsinmovies_main/index.html', context)


# class SearchAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return HistoryRecords.objects.none()
#
#         qs = HistoryRecords.objects.filter(owner=self.request.user).order_by('-date_added')
#
#         if self.q:
#             qs = qs.filter(query__istartswith=self.q)
#
#         return qs

def search(request):

    query = request.GET.get('q','')
    lang1 = request.GET.get('lang1','en')
    lang2 = request.GET.get('lang2','ru')
    page = request.GET.get('page', '1')
    res_per_page = request.GET.get('num', '25')

    if (not re.search('^[a-z]{2}$', lang1) or not re.search('^[a-z]{2}$', lang2)
        or not re.search('^[0-9]{1,10}$', page) or not re.search('^[0-9]{2,3}$', res_per_page)
        or not re.search('^[_\w\s\d\"\~\*\|\,\<=]{1,100}$', query)):
            return render(request, 'wordsinmovies_main/index.html',
            {'form':SearchForm(initial=blank_search_form),'error': 1, 'error_msg': 'Wrong query format.'})

    page = int(page)
    res_per_page = int(res_per_page)
    # sci_mode = (request.GET.get('sci_mode')=='True')
    pos_tags = (request.GET.get('pos_tags', 'False')=='True')

    form = SearchForm(initial={'query':query, 'lang1':lang1, 'lang2':lang2,
        'res_per_page':res_per_page, 'pos_tags':pos_tags})

    if not request.user.is_authenticated:
        ip = check_ip(request)
        if ip.n_requests == 0:
            return render(request, 'wordsinmovies_main/index.html',
            {'form': form, 'error': 1, 'error_msg': 'You have exceeded the day limit for your queries. Please, log in to continue your search.'})
        elif ip.last_query != query:
            ip.n_requests -= 1
            ip.last_query = query
            ip.save()
        # print(ip.n_requests)
    else:
        rup = request.user.profile
        if rup.n_requests == 0:
            return render(request, 'wordsinmovies_main/index.html',
            {'form': form, 'error': 1, 'error_msg': 'You have exceeded the day limit for your queries. You will be able to continue your search tomorrow.'})
        elif rup.last_query != query:
            rup.n_requests -= 1
            rup.last_query = query
            rup.save()
        # print(rup.n_requests)

    # results = QuerySphinx(query+lang1+lang2+str(start)+str(res_per_page))
    #number of the search result to begin with
    start = res_per_page * (page - 1)
    imdb_id = None

    try:
        results = QuerySphinx(sphinx_client, mydb, mydbcursor, query,
            lang1, lang2, start, res_per_page, pos_tags, imdb_id)
    except:
        return render(request, 'wordsinmovies_main/index.html',
            {'form': form, 'error': 1, 'error_msg': 'No matches found. Try again!'})


    if results['error_code']<0:
        print(lang2)
        return render(request, 'wordsinmovies_main/index.html',
            {'form': form, 'error': 1, 'error_msg': results['error_msg']})


    matches = results['matches'][0:res_per_page]
    total_found = results['total_found']

    total_pages = ceil(total_found/res_per_page)

    #starting page in the paginator
    min_page = ((page-1)//10)*10+1

    paginator = Paginator(  has_other_pages = (total_found > 0),
                            #has_previous = (page > 1),
                            #previous_page_number = max(page - 1, 1),
                            has_previous = (page > 10),
                            previous_page_number = max(min_page - 1, 1),
                            page_range = range(min_page, min(min_page+10, total_pages+1)),
                            number = page,
                            #has_next = (page < total_pages),
                            #next_page_number = min(page + 1, total_pages)
                            has_next = ((total_pages - min_page)>= 10),
                            next_page_number = min_page + 10,
                            )

    context = {'form': form, 'error':0, 'excerpts': matches, 'paginator': paginator,
    'languages': [lang1, lang2],'table_headers': [language_code[lang1], language_code[lang2]],
    'query': query, 'total_found':total_found, 'pos_tags':pos_tags}

    return render(request, 'wordsinmovies_main/index.html', context)
