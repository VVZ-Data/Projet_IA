""" Repository q-table"""

from .q_table import QTable
from .base import Base


class QTableRepo:

    def __init__(self, session):
        """
            Initialise le repository avec une session SQLAlchemy.
        """
        self.session = session
        self.cache: dict = {}



    def init_final_states(self, gama, learning_rate):
        """
            Initialise les état finaux du jeux dans la db
        """
        if self.session.query(QTable).filter(
            QTable.gama == gama,
            QTable.learning_rate == learning_rate,
            QTable.state.in_(["win", "lose"])
            ).count() == 0:

            self.session.add_all([
                QTable(gama=gama, learning_rate=learning_rate, state="win",  action_up=10, action_down=10, action_left=10, action_right=10),
                QTable(gama=gama, learning_rate=learning_rate,state="lose", action_up=-10, action_down=-10, action_left=-10, action_right=-10),
            ])
        self.session.commit()        

    
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
            return getattr(row, f"action_{action}", 0.0) or 0.0
        return 0.0

    def update_q_value(self, gama, learning_rate, state, action, new_value):
        key = (str(gama), str(learning_rate), state)
        row = self.cache.get(key) or self.session.get(QTable, key)
        if row:
            setattr(row, f"action_{action}", new_value)
            self.cache[key] = row  # met à jour le cache
        else:
            new_row = QTable(gama=str(gama), learning_rate=str(learning_rate), state=state, **{f"action_{action}": new_value})
            self.session.add(new_row)
            self.cache[key] = new_row
        self.session.flush()

    def commit(self):
        self.session.commit()