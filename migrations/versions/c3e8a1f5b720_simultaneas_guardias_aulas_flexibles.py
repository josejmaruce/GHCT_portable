"""Guardias por tipo, guardias requeridas por sesión, aula flexible, horas
seguidas por día y grupos oficiales de Bachillerato y FP.

- profesores: el tipo de guardia único (guardia_tipo) pasa a contarse por
  tipos: hasta 3 normales y hasta 3 extraordinarias repartidas entre patio,
  recreo activo, biblioteca en el recreo y biblioteca en hora de clase. Quien
  tenía una modalidad conserva lo que hacía el motor: 3 normales + 1 de ella.
  La columna guardia_tipo se queda en la tabla sin usar.
- guardias_requeridas: cuántas personas de guardia hacen falta en cada sesión.
  Va por día y hora de reloj, no por tramo de un turno, porque ESO,
  Bachillerato y FP tienen tramos distintos a la misma hora y la guardia es
  del centro.
- grupos_materia.aula_modo: fija (obligatoria), preferida (mejor, no
  obligatoria) o cualquiera.
- grupos_materia.max_horas_dia: sesiones seguidas que puede tener el mismo
  día. 1 para todos salvo la Familia Administrativo, que ya podía dar 2.
- grupos_materia.grupos_letras en Bachillerato y FP, sacado del código
  (B1-CT, B2-A, GAM1...), para poder sumar las horas de cada grupo.
- generaciones_horario.turnos_incluidos: los turnos con el mismo horario se
  generan juntos para que un profesor no esté en dos sitios a la vez.

SQL directo, como en las migraciones anteriores: batch_alter_table falla en
este proyecto con las claves ajenas sin nombre.

Revision ID: c3e8a1f5b720
Revises: a7c1d4e90b33
"""

import re

from alembic import op
import sqlalchemy as sa

revision = "c3e8a1f5b720"
down_revision = "a7c1d4e90b33"
branch_labels = None
depends_on = None


def _grupos_oficiales(codigo):
    cod = (codigo or "").upper()
    m = re.search(r"(GAM|SAB)([12])$", cod)
    if m:
        return [m.group(0)]
    m = re.search(r"(\d)ESO_?([A-D])$", cod)
    if m:
        return [m.group(1) + m.group(2)]
    tokens = [t for t in re.split(r"[-_ ]+", cod) if t]
    salida = []
    if "B1" in tokens or "B1CT" in tokens:
        if "CT" in tokens or "B1CT" in tokens:
            salida.append("B1-CT")
        if "HS" in tokens:
            salida.append("B1-HS")
    if "B2" in tokens:
        letras = [t for t in tokens[tokens.index("B2") :] if t in ("A", "B")]
        salida += [f"B2-{letra}" for letra in dict.fromkeys(letras)]
    return salida


def upgrade():
    for columna in (
        "guardias_normales",
        "guardias_recreo",
        "guardias_recreo_activo",
        "guardias_biblioteca_recreo",
        "guardias_biblioteca",
    ):
        op.execute(f"ALTER TABLE profesores ADD COLUMN {columna} INTEGER NOT NULL DEFAULT 0")
    op.execute("UPDATE profesores SET guardias_normales = 3 WHERE guardia_tipo IS NOT NULL")
    op.execute("UPDATE profesores SET guardias_recreo = 1 WHERE guardia_tipo = 'Recreo'")
    op.execute("UPDATE profesores SET guardias_recreo_activo = 1 WHERE guardia_tipo = 'Recreo activo'")
    op.execute("UPDATE profesores SET guardias_biblioteca_recreo = 1 WHERE guardia_tipo = 'Biblioteca'")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS guardias_requeridas (
            id INTEGER NOT NULL PRIMARY KEY,
            dia VARCHAR(1) NOT NULL,
            hora_inicio VARCHAR(5) NOT NULL,
            hora_fin VARCHAR(5) NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            cantidad INTEGER NOT NULL,
            CONSTRAINT uq_guardia_requerida UNIQUE (dia, hora_inicio, hora_fin, tipo)
        )
        """
    )

    op.execute("ALTER TABLE grupos_materia ADD COLUMN aula_modo VARCHAR(12) NOT NULL DEFAULT 'cualquiera'")
    op.execute("UPDATE grupos_materia SET aula_modo = 'fija' WHERE aula_requerida_id IS NOT NULL")
    op.execute("ALTER TABLE grupos_materia ADD COLUMN max_horas_dia INTEGER NOT NULL DEFAULT 1")
    op.execute(
        """
        UPDATE grupos_materia SET max_horas_dia = 2
        WHERE departamento_id IN (SELECT id FROM departamentos WHERE UPPER(nombre) LIKE '%ADMINISTRA%')
        """
    )

    conexion = op.get_bind()
    filas = conexion.execute(sa.text("SELECT id, codigo FROM grupos_materia WHERE grupos_letras IS NULL")).fetchall()
    for gm_id, codigo in filas:
        grupos = _grupos_oficiales(codigo)
        if grupos:
            conexion.execute(
                sa.text("UPDATE grupos_materia SET grupos_letras = :letras WHERE id = :id"),
                {"letras": ",".join(grupos), "id": gm_id},
            )

    op.execute("ALTER TABLE generaciones_horario ADD COLUMN turnos_incluidos VARCHAR(200)")


def downgrade():
    op.execute("ALTER TABLE generaciones_horario DROP COLUMN turnos_incluidos")
    op.execute("ALTER TABLE grupos_materia DROP COLUMN max_horas_dia")
    op.execute("ALTER TABLE grupos_materia DROP COLUMN aula_modo")
    op.execute("DROP TABLE IF EXISTS guardias_requeridas")
    for columna in (
        "guardias_biblioteca",
        "guardias_biblioteca_recreo",
        "guardias_recreo_activo",
        "guardias_recreo",
        "guardias_normales",
    ):
        op.execute(f"ALTER TABLE profesores DROP COLUMN {columna}")
