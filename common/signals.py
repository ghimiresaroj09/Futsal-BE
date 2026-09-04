import logging

from django.db.backends.signals import connection_created
from django.dispatch import receiver

logger = logging.getLogger("futsal.database")


@receiver(connection_created)
def log_database_connection(sender, connection, **kwargs):
    logger.info(
        "Database connection established: alias=%s backend=%s database=%s",
        connection.alias,
        connection.vendor,
        connection.settings_dict.get("NAME"),
    )
