"""Matrícula de STILUS: num_alumnos en grupo-materia y grafo de conflictos.

Del alumnado solo se guardan datos agregados: cuántos alumnos tiene cada
grupo-materia y qué parejas comparten alumnado. Ninguna identidad se persiste.

En SQLite se usa SQL directo en vez de batch_alter_table, que en este proyecto
falla al manejar las claves ajenas sin nombre.

Revision ID: a7c1d4e90b33
Revises: 46ce0f6b78a8
"""

from alembic import op

revision = "a7c1d4e90b33"
down_revision = "46ce0f6b78a8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE grupos_materia ADD COLUMN num_alumnos INTEGER")
    # La tabla puede existir ya: db.create_all() crea las tablas nuevas al
    # arrancar la app, y esta migración se escribió después.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS conflictos_grupo_materia (
            id INTEGER NOT NULL PRIMARY KEY,
            grupo_materia_a_id INTEGER NOT NULL REFERENCES grupos_materia (id),
            grupo_materia_b_id INTEGER NOT NULL REFERENCES grupos_materia (id),
            alumnos_comunes INTEGER NOT NULL,
            CONSTRAINT uq_conflicto_par UNIQUE (grupo_materia_a_id, grupo_materia_b_id)
        )
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS conflictos_grupo_materia")
    op.execute("ALTER TABLE grupos_materia DROP COLUMN num_alumnos")
