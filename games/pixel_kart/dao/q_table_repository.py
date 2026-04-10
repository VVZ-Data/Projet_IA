""" Repository q-table"""

from .q_table import QTable


class QTableRepo:

    def __init__(self, session):
        """
            Initialise le repository avec une session SQLAlchemy.
        """
        self.session = session
        self.cache: dict = {}
     
    
    def get_by_id(self, gama, learning_rate, state):
        """
            Retourne les 4 ligne possible 
        """

        return self.session.get(QTable, (str(gama), str(learning_rate), state))
    
    def get_q_value(self, gama, learning_rate, state, action):
        key = (str(gama), str(learning_rate), state)
        if key not in self.cache:  # lit la DB seulement si pas en cache
            row = self.session.get(QTable, key)
            self.cache[key] = row
        row = self.cache.get(key)
        if row:
            return getattr(row, f"{action}", 0.0) or 0.0
        return 0.0

    def update_q_value(self, gama, learning_rate, state, action, new_value):
        key = (str(gama), str(learning_rate), state)
        row = self.cache.get(key) or self.session.get(QTable, key)
        if row:
            setattr(row, f"action_{action}", new_value)
            self.cache[key] = row  # met à jour le cache
        else:
            new_row = QTable(gama=str(gama), learning_rate=str(learning_rate), state=state, **{f"{action}": new_value})
            self.session.add(new_row)
            self.cache[key] = new_row
        self.session.flush()

    def commit(self):
        self.session.commit()