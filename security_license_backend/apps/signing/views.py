from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from .models import SigningKey, Signature, Document
from .serializers import SigningKeySerializer, SignatureSerializer, DocumentSerializer


class SigningKeyViewSet(viewsets.ModelViewSet):
    queryset = SigningKey.objects.all()
    serializer_class = SigningKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propias claves
        return super().get_queryset().filter(user=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class SignatureViewSet(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['post'])
    def sign_document(self, request):
        # Endpoint personalizado para firmar
        doc_id = request.data.get('document_id')
        key_id = request.data.get('key_id')
        # Aquí llamaríamos al servicio de criptografía
        return Response({'status': 'signed', 'message': 'Lógica de firma pendiente de implementar'})