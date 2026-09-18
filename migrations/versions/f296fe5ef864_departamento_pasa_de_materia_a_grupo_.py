"""departamento pasa de materia a grupo-materia

Revision ID: f296fe5ef864
Revises: be5182ecbdf7
Create Date: 2026-09-09 20:09:42.531176

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f296fe5ef864'
down_revision = 'be5182ecbdf7'
branch_labels = None
depends_on = None


# SQLite >= 3.35 soporta ADD/DROP COLUMN directos; evitamos el modo "batch"
# de Alembic (recrea la tabla entera) porque su manejo de nombres de
# restricciones de clave foránea en SQLite es poco fiable.


def upgrade():
    op.execute("ALTER TABLE grupos_materia ADD COLUMN departamento_id INTEGER REFERENCES departamentos(id)")

    # Traslada el departamento que ya tuviera cada materia a TODOS sus
    # grupos-materia, como valor de partida editable por fila (el propio
    # usuario señaló que una misma materia, p.ej. MAE/CMAT/CLEN, puede
    # repartirse entre varios departamentos según el grupo concreto).
    op.execute(
        """
        UPDATE grupos_materia
        SET departamento_id = (
            SELECT materias.departamento_id FROM materias WHERE materias.id = grupos_materia.materia_id
        )
        WHERE EXISTS (
            SELECT 1 FROM materias
            WHERE materias.id = grupos_materia.materia_id AND materias.departamento_id IS NOT NULL
        )
        """
    )

    op.execute("ALTER TABLE materias DROP COLUMN departamento_id")


def downgrade():
    op.execute("ALTER TABLE materias ADD COLUMN departamento_id INTEGER REFERENCES departamentos(id)")
    op.execute(
        """
        UPDATE materias
        SET departamento_id = (
            SELECT gm.departamento_id FROM grupos_materia gm
            WHERE gm.materia_id = materias.id AND gm.departamento_id IS NOT NULL
            LIMIT 1
        )
        """
    )
    op.execute("ALTER TABLE grupos_materia DROP COLUMN departamento_id")
