===================
Django Job Board
===================

Job Board is a Django applicaiton that you can use in any django 3 software

Detailed documentation comming soon

Quick start
-----------

1. Add "polls" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'job_board',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('job_board/', include('job_board.urls')),

3. Run ``python manage.py migrate`` to create the job_board models.

4. Start the development server and visit http://127.0.0.1:8000/admin/

5. Visit http://127.0.0.1:8000/job_board/ to explore job_board.
6. Dependencies
   1. djangorestframework
   2. django-tinymce
   3. django-userforeignkey
   4. pillow and
   5. pyjwt