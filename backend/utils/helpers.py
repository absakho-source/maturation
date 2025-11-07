# ...existing code...
from datetime import datetime
from models import db, Log

def create_log(auteur: str, role: str, action: str, commentaire: str, statut: str, projet_id: int):
    l = Log(
        auteur=auteur,
        role=role,
        action=action,
        commentaire=commentaire,
        statut=statut,
        projet_id=projet_id,
        date=datetime.utcnow()
    )
    db.session.add(l)
    db.session.commit()
    return l