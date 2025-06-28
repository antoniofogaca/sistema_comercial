# core/management/commands/populate_empresas.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Empresa
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populates the database with dummy Empresa records for testing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            help='Number of dummy companies to create.',
            default=30, # Default to 30 if not specified
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Deletes all existing Empresa records before populating.',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear_existing = options['clear_existing']

        if clear_existing:
            self.stdout.write(self.style.WARNING("Deleting all existing Empresa records..."))
            Empresa.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing companies deleted."))

        self.stdout.write(self.style.MIGRATE_HEADING(f"Creating {count} dummy Empresa records..."))

        initial_id = Empresa.objects.count() + 1

        for i in range(initial_id, initial_id + count):
            cnpj_base = 10000000000000 + i
            cnpj = f"{cnpj_base:014d}"
            cnpj_formatted = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

            start_date = date.today() - timedelta(days=5 * 365)
            random_days = random.randint(0, 5 * 365)
            abertura_date = start_date + timedelta(days=random_days)

            porte_choices = [choice[0] for choice in Empresa.PORTE_CHOICES]
            situacao_choices = [choice[0] for choice in Empresa.SITUACAO_CHOICES]
            crt_choices = [choice[0] for choice in Empresa.CRT_CHOICES]

            try:
                Empresa.objects.create(
                    codigo_loja=f"LOJA{i:03d}",
                    cnpj=cnpj_formatted,
                    inscricao_estadual=f"{random.randint(100000000, 999999999)}",
                    porte=random.choice(porte_choices),
                    situacao=random.choice(situacao_choices),
                    data_abertura=abertura_date,
                    nome_empresa=f"Empresa Gerada {i} S.A.",
                    razao_social=f"Razao Social Gerada {i} LTDA",
                    fantasia=f"Fantasia Gerada {i}",
                    contato=f"Contato {i}",
                    telefone=f"(99) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    email=f"empresa.gerada.{i}@teste.com",
                    logradouro=f"Rua Gerada, {random.randint(1, 500)}",
                    numero=str(random.randint(1, 1000)),
                    bairro=f"Bairro {random.choice(['Centro Novo', 'Distrito Industrial', 'Vila Cidadania'])}",
                    cidade=f"Cidade Aleatória {random.choice(['D', 'E', 'F'])}",
                    uf=random.choice(['DF', 'GO', 'MT', 'MS', 'ES', 'RJ']),
                    cep=f"{random.randint(60000, 69999)}-{random.randint(100, 999)}",
                    cnae_principal=f"CNAE Gerado {random.randint(1000, 9999)}-{random.randint(1, 9)}",
                    aliquota_simples=round(random.uniform(1.0, 20.0), 2),
                    codigo_regime_tributario=random.choice(crt_choices),
                    cancelado=random.choice([True, False, False, False, False])
                )
                self.stdout.write(self.style.SUCCESS(f"Created Empresa Gerada {i} (CNPJ: {cnpj_formatted})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating company {i}: {e}"))

        total_empresas = Empresa.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\nFinished creating {count} dummy records."))
        self.stdout.write(self.style.WARNING(f"Total companies in the database now: {total_empresas}"))