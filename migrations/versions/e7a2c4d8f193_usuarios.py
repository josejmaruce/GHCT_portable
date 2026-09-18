"""Usuarios para entrar en la aplicación.

Revision ID: e7a2c4d8f193
Revises: d41f7b2c9e05
"""

from alembic import op

revision = "e7a2c4d8f193"
down_revision = "d41f7b2c9e05"
branch_labels = None
depends_on = None


def upgrade():
    # Puede existir ya: db.create_all() crea las tablas nuevas al arrancar.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER NOT NULL PRIMARY KEY,
            usuario VARCHAR(60) NOT NULL UNIQUE,
            nombre VARCHAR(120),
            hash_contrasena VARCHAR(255) NOT NULL,
            creado_en DATETIME
        )
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS usuarios")
