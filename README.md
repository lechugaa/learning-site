# Django Tutorial

In this document the necessary steps for building a Course Gallery Web Application will be described to be able to
replicate the implementation. The steps in here are mainly obtained from de [Treehouse Django Basics Course](https://teamtreehouse.com/library/django-basics).

## Building an App

To build an app once Django is installed, simply run `python manage.py startapp <name-of-app>` in the terminal. Afterwards,
in `settings.py` of the main project, the app should be included. Example of an app called courses:

```{python}
INSTALLED_APPS = [
    # other apps here have been omitted for simplicity
    'courses.apps.CoursesConfig',
]
```

It is also convenient in this same file to add the correct language for the web application and the adequate
`TIME_ZONE`.

## Creating Models

Example of a model named Course:

```
from django.db import models


# Create your models here.
class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=250)
    description = models.TextField()

    def __str__(self):
        return self.title

```

[More Django model field types.](https://docs.djangoproject.com/en/1.8/ref/models/fields/)

After creating a model it is necessary to migrate de database in order to include a table for this new model. This can 
be achieved by running the following commands:

### Ordering instances of a model

By default, the ordering of instances in a model will be done by using their primary key, which is a consecutive 
integer given by the database. The problem with this is that if we accidentally create something in disorder, it will
never be ordered this way as primary keys do not change and cannot be reduced.

To solve this issue we must add another property to the model that is an integer value an has the only purpose of
ordering instances of that model. Afterwards we need to create a `Meta` subclass inside the model to tell Django how
to order the instances. Here is an example:

```{python}
class Step(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)

    class Meta:
        ordering = ['order', ]
```

If two models have the same order value then the distinction is done lastly by primary key.

In the example above notice that we are adding a property to the model that has a value from another model. This is done
by using the `model.ForeignKey(<other-model>, on_delete)` command. It is important to add that if a `ForeignKey` model
is defined later in the code, the name of this model should be "quoted". 

### Creating a migration

In this case we will create a migration for the courses app where the Course model was created.

```{python}
# will make the migrations for a specific app
python manage.py makemigrations <app> 
```

```{python}
# will run the pending migrations for a specific app. If you leave off the app name, any pending migrations for any
# apps will be run.
python manage.py migrate <app>
```

### Adding model to admin console

Once a model is created, it is convenient to register models in admin console to be able to modify instances through
this helpful tool.

Example of registering the Course model in the admin console.

```{python}
# this must be done in the admin.py of the respective app
from django.contrib import admin
from .models import Course

admin.site.register(Course)
```

When we have a model that is an element of another model is a good idea to add a smaller form that represent another
inside the admin form for the model.

For example if we had a Class model that can contain a series of Steps model instances, we would first need to add an
inline.

```{ptyhon}
class StepInline(admin.StackedInline):
    model = Step
```

There are two types of inlines:
* StackedInline
* TabularInline

This creates the inline. After we need to create de admin. In this example a course admin:

```{python}
class CourseAdmin(admin.ModelAdmin):
    inlines = [StepInline]
```

Finally we have to register both the Course and the CourseAdmin:

```{python}
admin.site.register(Course, CourseAdmin)
```

## Creating a view

Example of creating a view that shows all available courses. This view simply returns a string with all the available courses.

```{python}
from django.http import HttpResponse
from django.shortcuts import render

from .models import Course


# Create your views here.
def course_list(request):
    courses = Course.objects.all()
    output = ', '.join([str(course) for course in courses])
    return HttpResponse(output)
```

### URLS

Once the view is created, it is necessary to add a `urls.py` file to the app. In it you must specify an URL path for
the newly created view. 

```{python}
from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list),
]
```

This can also be achieved with regular expressions instead of a hardwired path (i.e. ''').

Afterwards, this URLs must be migrated to the main project `urls.py` file. Example:

```{python}
from django.urls import path, include

urlpatterns = [
    # other paths here have been omitted for simplicity
    path('courses/', include('courses.urls')),
]
```

This will allow to go to `domain.com/courses/` to find the URLs defined there.

Sometimes we need an URL that can change for an instance of a model. An example is if we wanted to see the details of
a course, we would need a generic view for this but should render with the wanted object of the course.

This is achieved by the following notation:

```{python}
urlpatterns = [
    path('<int:pk>/', views.course_detail),
]
```

In this example the `int:pk` part will be substituted for an integer. To render a view that has a value involved, such as
a primary key, the `get_object_or_404(Course, pk=pk)` is very helpful. Even if we do not define explicitly a primary
key (i.e. pk) for a model, Django infers that this is what we want when we passed it as a value in the function.

To easily refer to urls in html code it is useful to add a name to such url. This is achieved with the following lines
of code:

```{python}
path('', views.hello_world, name='home')
```

This pattern can cause a problem that is the possibility of more than one app having the same names of an url. In order
to prevent this from happening, when we include those urls to the main project, we should add a namespace like this:

```{python}
path('courses/', include(('courses.urls', 'courses'), namespace='courses'))
```

Once we have defined names for our urls it is simple to use them in an anchor tag in an html file. Example:

```{html}
<h2><a href="{% url 'courses:detail' pk=step.course.pk %}">{{ step.course.title }}</a></h2>
```

```{html}
<h3><a href="{% url 'courses:step' course_pk=step.course.pk step_pk=step.pk %}">{{ step.title }}</a></h3>
```

```{html}
<header><a href="{% url 'courses:detail' pk=course.pk %}">{{ course.title }}</a></header>
```

Where the pattern `url '<namespace>:<url-name> <attributes>` emerge.

## Templates

By default, Django searches for the `templates` directory inside the `app` directory. It also expects another directory
inside the `templates` one with the same name as our app. In this case we should have:

* courses
    * templates
        * courses
        
In generic form it is:

* name-of-app
    * templates
        * name-of-app
    
Example of a template called `layout.html`:

```{html}
{%  for course in courses %}
    <h2>{{ course.title }}</h2>
    <p>{{ course.description }}</p>
{% endfor %}
```   

Once we have a parent template define, we can extend it in another template using `{% extends "layout.html" %}` at
the beginning of the new html file. Example:

```{html}
{% extends "layout.html" %}
{% block title %}Well, hello there!{% endblock %}
{% block content %}
    <h1>Welcome!</h1>
{% endblock %}
``` 

### Templates Inheritance

Example of a parent template

```{html}
<!doctype html>
<html>
    <head>
        <title>{% block title %}{% endblock %}</title>
    </head>
    <body>{% block content %}{% endblock %}</body>
</html>
```

## Static Assets

To add static content, we should add first of all a directory `assets`. In the main project settings file we have to add
a path to those static files with the following code:

```{python}
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
```

Afterwards in the `urls.py` file of the main project we have to add to the urlpatterns list the static file url patterns
with the following lines of code:

```{python}
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
```

This line will only be executed if in the settings we have set de DEBUG option to True. Otherwise we will have to use a 
server such as Apache to serve the static content instead of using python for these matters. This adds in DEBUG mode a
static path that points to all of our files in our static folders.

An example of a html file using these static files is:

```{html}
{% load static from staticfiles %}

<!doctype html>
<html>
    <head>
        <title>{% block title %}{% endblock %}</title>
        <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    </head>
    <div class="site-container">
        <body>{% block content %}{% endblock %}</body>
    </div>
</html>
```

### Making the a view use our template

For this task we will use the `render` function. Its parameters are:

* the request
* the path of the template as a string
* an optional dictionary specifying the key-value pairs that the html template expects

Example:

```{python}
from django.shortcuts import render
from .models import Course


# Create your views here.
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})
```

## Tests

Django includes a `tests.py` file in which we can include any tests that we want to perform to our code to ensure it 
work properly. 

Steps of testing:
1. Testing models
2. Testing views

Here is an example of a test:

```{python}
class CourseModelTest(TestCase):

    # test to see that the create now property is being defined correctly in our code
    def test_course_creation(self):
        course = Course.objects.create(
            title="Python Regular Expressions",
            description="Learn to write regular expressions in Python"
        )
        now = timezone.now()
        self.assertLess(course.created_at, now)
```

As you can notice, every model should have its own test class. Once all the tests have been defined, you can run them
with `python manage.py test` in the console. 

All functions that are meant to be a test should start their name with that word e.g. `test_example_given(self)`. You
can include other functions that help you perform some initial configurations. These should be named `setUp(self)` and
can only exist one per test class. 

Here is an example:

```{python}
class StepModelTest(TestCase):
    """testing the step model"""

    def setUp(self):
        self.course = Course.objects.create(
            title="Python Testing",
            description="Learn to write tests in Python."
        )

    def test_step_creation(self):
        step = Step.objects.create(
            title="Introduction to Doctests",
            description="Learn to write tests in your docstrings.",
            course=self.course
        )
        self.assertIn(step, self.course.step_set.all())
```

### Testing Views

To test views it is useful to use the context dictionary that the http request does to summon a view. An example is
given below:

```{python}
    def test_course_list_view(self):
        resp = self.client.get(reverse('courses:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.course, resp.context['courses'])
        self.assertIn(self.course2, resp.context['courses'])
```

In the example above we are using the `reverse` function from `django.urls`. It is worth mentioning that in the example
*courses* is the namespace given to the app and *list* is the name given to the view we are testing. 

Although it is generally preferred to test one thing per test class, urls and views are so related that it is a good 
idea to test both at the same time.

## Error Handling

### Return a 404 with a shortcut

There is a shortcut in Django to achieve a 404 in case that we do not have an object for the user's entered URL. This
shortcut is called `get_object_or_404` from the `django_shortcuts_library`. Here is an example of use:

```{python}
from django.shortcuts import render, get_object_or_404
from .models import Course

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/course_detail.html', {'course': course})
```

## Appendix A: Django manage.py commands

* `python manage.py startapp <app-name>` - creates an app
* `python manage.py makemigrations <app>` - creates migration for models in app
* `python manage.py migrate <app>` - executes migrations of an app
* `python manage.py shell` - enter Django's shell
* `python manage.py createsuperuser` - creates an admin user in Django project
* `python manage.py test` - runs tests created in `tests.py` for the corresponding model

More Django manage.py commands [here](https://docs.djangoproject.com/en/1.8/ref/django-admin/).
