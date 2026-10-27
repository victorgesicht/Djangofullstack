import time

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.generic import TemplateView, ListView, DetailView

from .models import Bulletins, IntelNote, TrainingOffering
from .forms import CommentForm, TrainingOfferForm


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


class TrainingView(ListView):
    model = TrainingOffering
    template_name = 'training.html'
    context_object_name = 'offerings'

    def get_queryset(self):
        return TrainingOffering.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('offer_form', TrainingOfferForm())
        selected = (
            self.request.GET.get('offering')
            or self.request.POST.get('offering_slug', '')
        )
        context['selected_offering'] = next(
            (o for o in context['offerings'] if o.slug == selected), None
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = TrainingOfferForm(request.POST)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(offer_form=form))

        # Honeypot: bots get a success page, nothing is stored.
        if form.cleaned_data.get('website'):
            return redirect(reverse('training') + '?sent=1#open-channel')

        now = time.time()
        last = request.session.get('training_offer_at', 0)
        if now - last < 15:
            messages.error(request, 'Transmission throttled. Try again in a few seconds.')
            return redirect(reverse('training') + '#open-channel')

        offer = form.save(commit=False)
        slug = strip_tags(request.POST.get('offering_slug', '')).strip()
        if slug:
            offer.offering = TrainingOffering.objects.filter(
                slug=slug, is_active=True
            ).first()
        offer.save()

        request.session['training_offer_at'] = now
        messages.success(request, 'Offer received. A human reviews every transmission.')
        return redirect(reverse('training') + '?sent=1#open-channel')