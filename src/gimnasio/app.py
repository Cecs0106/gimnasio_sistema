import tkinter as tk

from gimnasio.infrastructure.database import Database
from gimnasio.infrastructure.repositories.accesses_repo import AccessesRepository
from gimnasio.infrastructure.repositories.clients_repo import ClientsRepository
from gimnasio.infrastructure.repositories.payments_repo import PaymentsRepository
from gimnasio.services.accesses_service import AccessesService
from gimnasio.services.clients_service import ClientsService
from gimnasio.services.payments_service import PaymentsService
from gimnasio.services.reports_service import ReportsService
from gimnasio.services.settings_service import SettingsService
from gimnasio.ui.main_window import MainWindow


def build_dependencies():
    database = Database()
    clients_repo = ClientsRepository(database)
    payments_repo = PaymentsRepository(database)
    accesses_repo = AccessesRepository(database)

    clients_service = ClientsService(clients_repo, payments_repo)
    payments_service = PaymentsService(payments_repo, clients_repo)
    accesses_service = AccessesService(clients_repo, payments_repo, accesses_repo)
    reports_service = ReportsService(clients_service, payments_service, accesses_service)
    settings_service = SettingsService(database)

    return {
        "clients_service": clients_service,
        "payments_service": payments_service,
        "accesses_service": accesses_service,
        "reports_service": reports_service,
        "settings_service": settings_service,
    }


def main():
    root = tk.Tk()
    dependencies = build_dependencies()
    MainWindow(root, dependencies)
    root.mainloop()


if __name__ == "__main__":
    main()
