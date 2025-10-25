from django.shortcuts import redirect, HttpResponse



class LoginPageRedirectMiddleware:
    """
    Middleware to redirect authenticated users away from the login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view before it is called.
        """
        if request.resolver_match.url_name in ['login_view']:
            if not request.user.is_authenticated:
                return None
            else:
                return redirect('users:dashboard_view')
            
        if request.resolver_match.url_name in ['dashboard_view']:
            if request.user.is_authenticated:
                return None
            else:
                return redirect('users:login_view')