from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import validate_email
from django.db import DatabaseError
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import PortfolioDocument, PortfolioExperience, PortfolioProfile, PortfolioSkill


PROFILE = {
    'name': 'Kashish',
    'role': 'Civil Engineering Professional',
    'summary': (
        'Civil Engineering professional focused on site execution, structural planning, '
        'quantity estimation, quality control, and efficient project delivery across diverse construction projects.'
    ),
    'contact': {
        'location': 'India',
        'email': 'Add your email',
    },
    'skills': [
        'AutoCAD drawings',
        'Quantity estimation',
        'Site supervision',
        'Construction planning',
        'Surveying basics',
        'Concrete and RCC work',
        'Project documentation',
        'Quality and safety checks',
    ],
    'experience': [
        {
            'title': 'Civil Engineering Portfolio',
            'meta': 'Resume-based presentation',
            'points': [
                'Prepared to present resume, civil engineering strengths, and downloadable project documents in one place.',
                'Highlights practical civil engineering work such as drawings, estimation, planning, and execution support.',
                'Includes backend-managed PDF uploads so the latest resume and drawing files can be replaced without editing code.',
            ],
        }
    ],
    'projects': [
        {
            'name': 'Civil Drawing Package',
            'description': 'A downloadable PDF drawing can be uploaded from the backend and shared directly with visitors.',
        },
        {
            'name': 'Resume Portfolio',
            'description': 'A clean personal presentation page that turns resume information into a professional web profile.',
        },
    ],
}


def _profile():
    profile, _ = PortfolioProfile.objects.get_or_create(pk=1)
    return profile


def _profile_payload():
    payload = PROFILE.copy()
    payload['contact'] = PROFILE['contact'].copy()
    saved_profile = _profile()
    payload['contact']['email'] = saved_profile.email or 'Add your email'

    skills = PortfolioSkill.objects.filter(is_visible=True)
    if skills.exists():
        payload['skills'] = [skill.name for skill in skills]

    experiences = PortfolioExperience.objects.filter(is_visible=True)
    if experiences.exists():
        payload['experience'] = [
            {
                'title': experience.title,
                'meta': experience.meta,
                'points': experience.point_list(),
            }
            for experience in experiences
        ]
    return payload


def _latest_document(document_type):
    document = PortfolioDocument.objects.filter(document_type=document_type).first()
    if document:
        return {
            'title': document.title,
            'url': document.file.url,
            'uploadedAt': document.uploaded_at.isoformat(),
        }

    fallback = settings.MEDIA_ROOT / 'documents' / f'{document_type}.pdf'
    if fallback.exists():
        return {
            'title': 'Resume' if document_type == PortfolioDocument.RESUME else 'PDF Drawing',
            'url': f'{settings.MEDIA_URL}documents/{document_type}.pdf',
            'uploadedAt': None,
        }

    return None


@ensure_csrf_cookie
def home(request):
    return render(request, 'portfolio/home.html')


def profile_data(request):
    try:
        profile = _profile_payload()
        documents = {
            'resume': _latest_document(PortfolioDocument.RESUME),
            'drawing': _latest_document(PortfolioDocument.DRAWING),
        }
    except DatabaseError:
        profile = PROFILE.copy()
        profile['contact'] = PROFILE['contact'].copy()
        documents = {
            'resume': None,
            'drawing': None,
        }

    return JsonResponse({
        'profile': profile,
        'documents': documents,
    })


def _validate_pdf(uploaded_file):
    extension = Path(uploaded_file.name).suffix.lower()
    if extension != '.pdf' or uploaded_file.content_type not in {'application/pdf', 'application/octet-stream'}:
        raise ValidationError('Only PDF files are allowed.')


def _backend_password():
    return getattr(settings, 'BACKEND_PASSWORD', None) or 'kashish123'


def _render_backend_login(request, error=''):
    return render(request, 'portfolio/backend_login.html', {
        'error': error,
    })


def _backend_context(message='', error=''):
    try:
        profile = _profile()
        skills = list(PortfolioSkill.objects.all())
        experiences = list(PortfolioExperience.objects.all())
        documents = {
            'resume': _latest_document(PortfolioDocument.RESUME),
            'drawing': _latest_document(PortfolioDocument.DRAWING),
        }
    except DatabaseError:
        profile = type('ProfileFallback', (), {'email': ''})()
        skills = []
        experiences = []
        documents = {
            'resume': None,
            'drawing': None,
        }
        error = error or 'Database tables are not ready yet. Redeploy on Railway so migrations can run.'

    return {
        'message': message,
        'error': error,
        'profile': profile,
        'skills': skills,
        'experiences': experiences,
        'documents': documents,
    }


@require_http_methods(['GET', 'POST'])
def upload_documents(request):
    message = ''
    error = ''

    if request.POST.get('action') == 'logout':
        request.session.pop('backend_authenticated', None)
        return _render_backend_login(request)

    if not request.session.get('backend_authenticated'):
        if request.method == 'POST' and request.POST.get('action') == 'login':
            if request.POST.get('password') == _backend_password():
                request.session['backend_authenticated'] = True
            else:
                return _render_backend_login(request, 'Incorrect password.')
        else:
            return _render_backend_login(request)

    if request.method == 'POST':
        action = request.POST.get('action', 'document')

        if action == 'profile':
            email = request.POST.get('email', '').strip()
            try:
                if email:
                    validate_email(email)
                profile = _profile()
                profile.email = email
                profile.save(update_fields=['email', 'updated_at'])
                message = 'Email updated successfully.'
            except ValidationError:
                error = 'Enter a valid email address.'
            except DatabaseError:
                error = 'Could not save email because the database is not ready. Redeploy so migrations can run.'
        elif action == 'experience':
            title = request.POST.get('title', '').strip()
            meta = request.POST.get('meta', '').strip()
            points = request.POST.get('points', '').strip()

            if not title:
                error = 'Enter an experience title.'
            elif not points:
                error = 'Enter at least one experience point.'
            else:
                try:
                    display_order = PortfolioExperience.objects.count() + 1
                    PortfolioExperience.objects.create(
                        title=title,
                        meta=meta,
                        points=points,
                        display_order=display_order,
                    )
                    message = 'Experience added successfully.'
                except DatabaseError:
                    error = 'Could not add experience because the database is not ready. Redeploy so migrations can run.'
        elif action == 'delete_experience':
            try:
                PortfolioExperience.objects.filter(pk=request.POST.get('experience_id')).delete()
                message = 'Experience deleted successfully.'
            except DatabaseError:
                error = 'Could not delete experience because the database is not ready.'
        elif action == 'skill':
            name = request.POST.get('name', '').strip()

            if not name:
                error = 'Enter a skill name.'
            else:
                try:
                    display_order = PortfolioSkill.objects.count() + 1
                    PortfolioSkill.objects.create(
                        name=name,
                        display_order=display_order,
                    )
                    message = 'Skill added successfully.'
                except DatabaseError:
                    error = 'Could not add skill because the database is not ready. Redeploy so migrations can run.'
        elif action == 'delete_skill':
            try:
                PortfolioSkill.objects.filter(pk=request.POST.get('skill_id')).delete()
                message = 'Skill deleted successfully.'
            except DatabaseError:
                error = 'Could not delete skill because the database is not ready.'
        else:
            document_type = request.POST.get('document_type')
            uploaded_file = request.FILES.get('file')

            if document_type not in {PortfolioDocument.RESUME, PortfolioDocument.DRAWING}:
                error = 'Choose a valid document type.'
            elif not uploaded_file:
                error = 'Choose a PDF file to upload.'
            else:
                try:
                    _validate_pdf(uploaded_file)
                    title = 'Resume' if document_type == PortfolioDocument.RESUME else 'PDF Drawing'
                    path = default_storage.save(f'documents/{document_type}.pdf', uploaded_file)
                    PortfolioDocument.objects.create(
                        title=title,
                        document_type=document_type,
                        file=path,
                    )
                    message = f'{title} uploaded successfully.'
                except ValidationError as exc:
                    error = exc.messages[0]
                except DatabaseError:
                    error = 'Could not save document because the database is not ready. Redeploy so migrations can run.'

    return render(request, 'portfolio/upload.html', _backend_context(message, error))
