from django.views.generic.base import TemplateView
from django.views.generic.edit import View
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth.models import User

from allauth.account.forms import LoginForm #, SignupForm


class AnonymousHomeView(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(AnonymousHomeView, self).get_context_data(**kwargs)
        context["form"] = LoginForm()
        return context

class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('anonymoushome'))



# class SignupView(TemplateView):
#     template_name = 'signup.html'

#     def get_context_data(self, **kwargs):
#         context = super(SignupView, self).get_context_data(**kwargs)
#         context["form"] = SignupForm()
#         return context