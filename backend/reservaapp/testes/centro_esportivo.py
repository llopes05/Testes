from django.test import TestCase
from rest_framework.test import APIClient
import json
from django.contrib.auth import get_user_model
from reservaapp.models import CentroEsportivo, EspacoEsportivo
from reservaapp.serializers import CentroEsportivoSerializer
from rest_framework.request import Request
from django.test import RequestFactory



class TesteModelos(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.centro = CentroEsportivo.objects.create(
            nome='Centro Esportivo Teste',
            foto_perfil='fkdlfkdl',
            foto_capa='fdsfsfds',
            descricao='Centro de esportes para testes',
            latitude=-23.55052,
            longitude=-46.633308,
            cidade='São Paulo',
            UF='RN',
            gerente=self.user,

            
        )
        

    def test_criacao_centro_esportivo(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, 'fdsfsfds')


    def test_criacao_centro_esportivo_cidade(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, '')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, 'fdsfsfds')
    
    def test_criacao_centro_esportivo_uf(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, 'fdsfsfds')
    
    def test_criacao_centro_esportivo_gerente(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, '')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, 'fdsfsfds')

    def test_criacao_centro_esportivo_descricao(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, '')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, 'fdsfsfds')

    def test_criacao_centro_esportivo_latitude(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), )
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, 'fdsfsfds')

    def test_criacao_centro_esportivo_longitude(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), )
        self.assertEqual(centro.foto_capa, 'fdsfsfds')

    def test_criacao_centro_esportivo_fotocapa(self):
        centro = CentroEsportivo.objects.get(nome='Centro Esportivo Teste')
        self.assertEqual(centro.cidade, 'São Paulo')
        self.assertEqual(centro.UF, 'RN')
        self.assertEqual(centro.gerente.username, 'testuser')
        self.assertEqual(centro.descricao, 'Centro de esportes para testes')
        self.assertEqual(float(centro.latitude), -23.55052)
        self.assertEqual(float(centro.longitude), -46.633308)
        self.assertEqual(centro.foto_capa, '')


class TesteSerializerCentroEsportivo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            tipo='gerente'
        )
        self.centro_data = {
            'nome': 'Centro Esportivo Serializer Teste',
            'descricao': 'Centro para testes de serializer',
            'cidade': 'Natal',
            'UF': 'RN',
            'latitude': -5.7945,
            'longitude': -35.2110
        }

    def test_serializacao_centro_esportivo_valido(self):
        """Teste se o serializer serializa dados válidos corretamente"""
        centro = CentroEsportivo.objects.create(
            gerente=self.user,
            **self.centro_data
        )
        
        request = self.factory.get('/')
        serializer = CentroEsportivoSerializer(centro, context={'request': Request(request)})
        
        data = serializer.data
        self.assertEqual(data['nome'], 'Centro Esportivo Serializer Teste')
        self.assertEqual(data['cidade'], 'Natal')
        self.assertEqual(data['UF'], 'RN')
        self.assertEqual(float(data['latitude']), -5.7945)
        self.assertEqual(float(data['longitude']), -35.2110)
        self.assertIn('id', data)
        self.assertIn('media_avaliacao', data)

    def test_desserializacao_dados_validos(self):
        """Teste se o serializer deserializa dados válidos corretamente"""
        serializer = CentroEsportivoSerializer(data=self.centro_data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['nome'], 'Centro Esportivo Serializer Teste')
        self.assertEqual(serializer.validated_data['cidade'], 'Natal')

    def test_validacao_nome_obrigatorio(self):
        """Teste se o serializer valida que o nome é obrigatório"""
        data_sem_nome = self.centro_data.copy()
        del data_sem_nome['nome']
        
        serializer = CentroEsportivoSerializer(data=data_sem_nome)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('nome', serializer.errors)

    def test_validacao_cidade_obrigatoria(self):
        """Teste se o serializer valida que a cidade é obrigatória"""
        data_sem_cidade = self.centro_data.copy()
        del data_sem_cidade['cidade']
        
        serializer = CentroEsportivoSerializer(data=data_sem_cidade)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('cidade', serializer.errors)

    def test_validacao_uf_obrigatoria(self):
        """Teste se o serializer valida que a UF é obrigatória"""
        data_sem_uf = self.centro_data.copy()
        del data_sem_uf['UF']
        
        serializer = CentroEsportivoSerializer(data=data_sem_uf)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('UF', serializer.errors)

    def test_validacao_latitude_obrigatoria(self):
        """Teste se o serializer valida que a latitude é obrigatória"""
        data_sem_latitude = self.centro_data.copy()
        del data_sem_latitude['latitude']
        
        serializer = CentroEsportivoSerializer(data=data_sem_latitude)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)

    def test_validacao_longitude_obrigatoria(self):
        """Teste se o serializer valida que a longitude é obrigatória"""
        data_sem_longitude = self.centro_data.copy()
        del data_sem_longitude['longitude']
        
        serializer = CentroEsportivoSerializer(data=data_sem_longitude)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('longitude', serializer.errors)

    def test_validacao_centro_duplicado(self):
        """Teste se o serializer valida centros com mesmo nome, cidade e UF"""
        CentroEsportivo.objects.create(
            gerente=self.user,
            **self.centro_data
        )
        
        serializer = CentroEsportivoSerializer(data=self.centro_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn('Já existe um centro esportivo', str(serializer.errors))

    def test_campos_read_only(self):
        """Teste se campos read_only não são aceitos na deserialização"""
        data_com_read_only = self.centro_data.copy()
        data_com_read_only['id'] = 999
        data_com_read_only['media_avaliacao'] = 5.0
        
        serializer = CentroEsportivoSerializer(data=data_com_read_only)
        
        self.assertTrue(serializer.is_valid())
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('media_avaliacao', serializer.validated_data)

    def test_urls_fotos_com_request_context(self):
        """Teste se as URLs das fotos são geradas corretamente com contexto de request"""
        centro = CentroEsportivo.objects.create(
            gerente=self.user,
            **self.centro_data
        )
        
        request = self.factory.get('/')
        serializer = CentroEsportivoSerializer(centro, context={'request': Request(request)})
        
        data = serializer.data
        self.assertIsNone(data.get('foto_perfil_url'))
        self.assertIsNone(data.get('foto_capa_url'))

    def test_urls_fotos_sem_request_context(self):
        """Teste se as URLs das fotos são None sem contexto de request"""
        centro = CentroEsportivo.objects.create(
            gerente=self.user,
            **self.centro_data
        )
        
        serializer = CentroEsportivoSerializer(centro)
        
        data = serializer.data
        self.assertIsNone(data.get('foto_perfil_url'))
        self.assertIsNone(data.get('foto_capa_url'))




    