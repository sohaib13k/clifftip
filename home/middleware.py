from django.shortcuts import redirect, render

class RedirectToNewDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return render(request, "home/domain_redirect.html")