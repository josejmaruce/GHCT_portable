"""Sustituciones: un profesor de baja y quien le sustituye.

Mientras dura, las asignaturas, reuniones, cargos elegidos y sesiones de
horario ya generadas del titular pasan a quien le sustituye. Se guarda qué se
movió para devolverlo exactamente al reincorporarse.

Revision ID: d41f7b2c9e05
Revises: c3e8a1f5b720
"""

from alembic import op

revision = "d41f7b2c9e05"
down_revision = "c3e8a1f5b720"
branch_labels = None
depends_on = None


def upgrade():
    # Puede existir ya: db.create_all() crea las tablas nuevas al arrancar.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS sustituciones (
            id INTEGER NOT NULL PRIMARY KEY,
            titular_id INTEGER NOT NULL REFERENCES profesores (id),
            sustituto_id INTEGER NOT NULL REFERENCES profesores (id),
            fecha_inicio DATE,
            fecha_fin DATE,
            activa BOOLEAN NOT NULL DEFAULT 1,
            asignaciones_movidas TEXT,
            cargos_movidos TEXT,
            reuniones_movidas TEXT,
            sesiones_movidas TEXT
        )
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS sustituciones")
