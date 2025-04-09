from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from members.models import Document
from api.serializers import DocumentSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class DocumentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        self.document = Document.objects.create(
            title='Test Document',
            description='Test Description',
            category='General',
            file=SimpleUploadedFile("test.pdf", b"file_content")
        )
        self.url = reverse('document-list')

    def test_list_documents(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_document_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'New Document',
            'description': 'New Description',
            'category': 'General',
            'file': SimpleUploadedFile("new.pdf", b"file_content")
        }
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_increment_downloads(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('document-increment-downloads', 
                     kwargs={'pk': self.document.pk})
        initial_count = self.document.download_count
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.document.refresh_from_db()
        self.assertEqual(self.document.download_count, initial_count + 1) 