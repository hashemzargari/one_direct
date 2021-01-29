def url_validator(url):
    from django import forms
    from django.core.exceptions import ValidationError
    try:
        f = forms.URLField()
        return f.clean(url)
    except ValidationError:
        return False
