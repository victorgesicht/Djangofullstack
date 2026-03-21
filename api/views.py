from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.http import Http404
from .models  import Bulletins, IntelNote
# Create your views here.
# profile---name""/etc/profile"
#blog/feed--/var/log

#breadcrumb-home>logs>post
#dev/null-404


class Index(ListView):
    model=Bulletins
    template_name='index.html'
    context_object_name='bulletins'



class profile(View):
    template_name='profile.html'


class BulletinsListView(ListView):
    model = Bulletins
    template_name = "bulletins.html"
#I dont trust its very complete
    def get(self,request,*args,**kwargs):
        queryset=self.get_queryset()

        if not queryset.exists():
            raise Http404("No records...")

        return super().get(request,*args,**kwargs)


    def post(self,request, *args, **kwargs):
        ...



class BulletingDetailView(DetailView):
    template_name='bulletin.html'
    model = Bulletins


class IntelDetailView(DetailView):
    template_name='intel.html'
    model=IntelNote

class IntelNotes(TemplateView):
    template_name='Inotes.html'
    model=IntelNote