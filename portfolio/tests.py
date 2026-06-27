import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import PortfolioDocument, PortfolioExperience, PortfolioProfile, PortfolioSkill


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=Path(TEST_MEDIA_ROOT))
class PortfolioViewsTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username='admin',
            password='password',
            is_staff=True,
        )

    def test_home_renders_react_mount(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="root"')

    def test_profile_api_returns_resume_fallback(self):
        PortfolioProfile.objects.create(pk=1, email='kashish@example.com')

        response = self.client.get(reverse('profile-data'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['profile']['role'], 'Civil Engineering Professional')
        self.assertEqual(payload['profile']['contact']['email'], 'kashish@example.com')
        self.assertIn('resume', payload['documents'])

    def test_backend_updates_profile_email(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(reverse('upload-documents'), {
            'action': 'profile',
            'email': 'new.email@example.com',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email updated successfully.')
        self.assertEqual(PortfolioProfile.objects.get(pk=1).email, 'new.email@example.com')

    def test_backend_adds_experience(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(reverse('upload-documents'), {
            'action': 'experience',
            'title': 'Site Engineer Intern',
            'meta': 'ABC Construction - 2025',
            'points': 'Managed site measurements\nPrepared daily progress notes',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Experience added successfully.')
        experience = PortfolioExperience.objects.get()
        self.assertEqual(experience.title, 'Site Engineer Intern')
        self.assertEqual(experience.point_list(), ['Managed site measurements', 'Prepared daily progress notes'])

    def test_profile_api_returns_backend_experience(self):
        PortfolioExperience.objects.create(
            title='Site Engineer Intern',
            meta='ABC Construction - 2025',
            points='Managed site measurements\nPrepared daily progress notes',
        )

        response = self.client.get(reverse('profile-data'))

        self.assertEqual(response.status_code, 200)
        experience = response.json()['profile']['experience'][0]
        self.assertEqual(experience['title'], 'Site Engineer Intern')
        self.assertEqual(experience['points'], ['Managed site measurements', 'Prepared daily progress notes'])

    def test_backend_adds_and_deletes_skill(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(reverse('upload-documents'), {
            'action': 'skill',
            'name': 'AutoCAD',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Skill added successfully.')
        skill = PortfolioSkill.objects.get()

        response = self.client.post(reverse('upload-documents'), {
            'action': 'delete_skill',
            'skill_id': skill.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Skill deleted successfully.')
        self.assertFalse(PortfolioSkill.objects.exists())

    def test_backend_deletes_experience(self):
        self.client.force_login(self.staff_user)
        experience = PortfolioExperience.objects.create(
            title='Site Engineer Intern',
            points='Managed site measurements',
        )

        response = self.client.post(reverse('upload-documents'), {
            'action': 'delete_experience',
            'experience_id': experience.id,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Experience deleted successfully.')
        self.assertFalse(PortfolioExperience.objects.exists())

    def test_profile_api_returns_backend_skills(self):
        PortfolioSkill.objects.create(name='AutoCAD')
        PortfolioSkill.objects.create(name='Quantity estimation')

        response = self.client.get(reverse('profile-data'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['profile']['skills'], ['AutoCAD', 'Quantity estimation'])

    def test_upload_accepts_pdf_document(self):
        self.client.force_login(self.staff_user)
        upload = SimpleUploadedFile('drawing.pdf', b'%PDF-1.4 test', content_type='application/pdf')

        response = self.client.post(reverse('upload-documents'), {
            'document_type': PortfolioDocument.DRAWING,
            'file': upload,
        })

        self.assertEqual(response.status_code, 200)
        document = PortfolioDocument.objects.get(document_type=PortfolioDocument.DRAWING)
        self.assertEqual(document.file_data, b'%PDF-1.4 test')

    def test_profile_api_returns_download_endpoint_for_uploaded_document(self):
        PortfolioDocument.objects.create(
            title='PDF Drawing',
            document_type=PortfolioDocument.DRAWING,
            file='documents/drawing.pdf',
            file_data=b'%PDF-1.4 test',
        )

        response = self.client.get(reverse('profile-data'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['documents']['drawing']['url'],
            reverse('download-document', args=[PortfolioDocument.DRAWING]),
        )

    def test_download_document_returns_pdf_attachment(self):
        PortfolioDocument.objects.create(
            title='PDF Drawing',
            document_type=PortfolioDocument.DRAWING,
            file='documents/drawing.pdf',
            file_data=b'%PDF-1.4 test',
        )

        response = self.client.get(reverse('download-document', args=[PortfolioDocument.DRAWING]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.4 test')

    def test_upload_rejects_non_pdf_document(self):
        self.client.force_login(self.staff_user)
        upload = SimpleUploadedFile('drawing.txt', b'not a pdf', content_type='text/plain')

        response = self.client.post(reverse('upload-documents'), {
            'document_type': PortfolioDocument.DRAWING,
            'file': upload,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only PDF files are allowed.')
        self.assertFalse(PortfolioDocument.objects.exists())
