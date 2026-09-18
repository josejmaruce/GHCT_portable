"""motor: turno/aula en grupo-materia, reuniones, resultado del horario

Revision ID: 98aee423a2cc
Revises: 559459c93210
Create Date: 2026-09-09 23:54:01.833254

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '98aee423a2cc'
down_revision = '559459c93210'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE grupos_materia ADD COLUMN turno_id INTEGER REFERENCES turnos(id)")
    op.execute("ALTER TABLE grupos_materia ADD COLUMN aula_requerida_id INTEGER REFERENCES aulas(id)")


def downgrade():
    op.execute("ALTER TABLE grupos_materia DROP COLUMN aula_requerida_id")
    op.execute("ALTER TABLE grupos_materia DROP COLUMN turno_id")
