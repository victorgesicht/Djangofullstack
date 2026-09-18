from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import redirect
from .models import Bulletins, IntelNote
from .forms import CommentForm


class Index(ListView):
    model = Bulletins
    template_name = 'index.html'
    context_object_name = 'writeups'
    paginate_by = None


class Writeups(ListView):
    model = Bulletins
    template_name = 'bulletins.html'
    context_object_name = 'writeups'
    paginate_by = None

    def get_queryset(self):
        return Bulletins.objects.all().order_by('-publication_date')


class WriteUpDetailView(DetailView):
    model = Bulletins
    template_name = 'bulletin.html'
    context_object_name = 'writeup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(data=request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = self.object
            new_comment.save()
            return redirect(self.request.path)

        return self.render_to_response(self.get_context_data(comment_form=form))


class IntelDetailView(DetailView):
    template_name = 'intel.html'
    model = IntelNote


class IntelNotes(TemplateView):
    template_name = 'Inotes.html'
    model = IntelNote


class Lboard(TemplateView):
    template_name = 'L-boards.html'