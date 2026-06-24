"""splitter user.nom en prenom + nom_famille

Revision ID: 5adbe995518e
Revises: 755d4b8c5f3e
Create Date: 2026-06-23 14:57:37.974973

Refactor du modèle User : le champ unique 'nom' (libre format) est remplacé
par deux champs distincts 'prenom' et 'nom_famille', cohérents avec le
modèle Profil et l'algorithme de numérologie.

Stratégie sûre pour les environnements avec données existantes :
1. Ajout des nouvelles colonnes en NULLABLE
2. Backfill : split de 'nom' au premier espace
   - "Jean Dupont" → prenom="Jean", nom_famille="Dupont"
   - "Mononyme"    → prenom="Mononyme", nom_famille="-"
3. Passage en NOT NULL
4. Suppression de l'ancienne colonne 'nom'

Le downgrade reconstitue 'nom' à partir des deux champs (concaténation).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5adbe995518e'
down_revision: Union[str, None] = '755d4b8c5f3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ajouter les colonnes en NULLABLE pour permettre le backfill
    op.add_column('users', sa.Column('prenom', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('nom_famille', sa.String(length=100), nullable=True))

    # 2. Backfill : split au premier espace
    #    - "Jean Dupont"   → prenom="Jean", nom_famille="Dupont"
    #    - "Jean-Marc Du Pont" → prenom="Jean-Marc", nom_famille="Du Pont"
    #    - "Mononyme"      → prenom="Mononyme", nom_famille="-"
    op.execute("""
        UPDATE users
        SET
            prenom = CASE
                WHEN POSITION(' ' IN nom) > 0 THEN SUBSTRING(nom FROM 1 FOR POSITION(' ' IN nom) - 1)
                ELSE nom
            END,
            nom_famille = CASE
                WHEN POSITION(' ' IN nom) > 0 THEN SUBSTRING(nom FROM POSITION(' ' IN nom) + 1)
                ELSE '-'
            END
    """)

    # 3. Rendre NOT NULL maintenant que toutes les lignes sont renseignées
    op.alter_column('users', 'prenom', nullable=False)
    op.alter_column('users', 'nom_famille', nullable=False)

    # 4. Supprimer l'ancienne colonne
    op.drop_column('users', 'nom')


def downgrade() -> None:
    # Reconstituer 'nom' par concaténation, en évitant le placeholder '-'
    op.add_column('users', sa.Column('nom', sa.VARCHAR(length=100), nullable=True))
    op.execute("""
        UPDATE users
        SET nom = CASE
            WHEN nom_famille = '-' THEN prenom
            ELSE prenom || ' ' || nom_famille
        END
    """)
    op.alter_column('users', 'nom', nullable=False)
    op.drop_column('users', 'nom_famille')
    op.drop_column('users', 'prenom')
