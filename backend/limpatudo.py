import os
import shutil
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reserva.settings")
django.setup()

from django.contrib.auth import get_user_model
from reservaapp.models import CentroEsportivo, EspacoEsportivo, Agenda, Reserva, Pagamento  # noqa: E402

User = get_user_model()


def limpar_banco():
    print("🧹 Limpando banco de dados...")
    Pagamento.objects.all().delete()
    Reserva.objects.all().delete()
    Agenda.objects.all().delete()
    EspacoEsportivo.objects.all().delete()
    CentroEsportivo.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()
    print("✨ Banco limpo!")


def limpar_midia():
    print("🧽 Limpando pastas de mídia...")
    base_dir = Path(__file__).resolve().parent
    media_dir = base_dir / "media"
    pastas = [
        media_dir / "comprovantes",
        media_dir / "centros_capa",
        media_dir / "centros_perfil",
        media_dir / "espacos_capa",
        media_dir / "espacos_perfil",
        media_dir / "espacos_foto1",
        media_dir / "espacos_foto2",
        media_dir / "espacos_foto3",
        media_dir / "espacos_foto4",
    ]
    for pasta in pastas:
        if pasta.exists():
            shutil.rmtree(pasta, ignore_errors=True)
        pasta.mkdir(parents=True, exist_ok=True)
    print("🧼 Pastas de mídia limpas!")


def main():
    limpar_banco()
    limpar_midia()


if __name__ == "__main__":
    main()
