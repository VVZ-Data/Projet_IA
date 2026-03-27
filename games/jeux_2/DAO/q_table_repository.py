""" Repository q-table"""

from DAO.q_table import QTable

class QTableRepo:

    def __init__(self, session):
        """
            Initialise le repository avec une session SQLAlchemy.
        """    
        self.session = session

    def create(self, gama, lr, state, action_up, action_down, action_left, action_right):
        """
            crée et retourne une q-table
        """
        q_table = QTable((gama, lr), state, action_up, action_down, action_left, action_right)
        self.session.add(q_table)
        self.session.commit()

    def get_by_id(self, id):
        """
            Retourne une q-table en fonction de son id, None si inexistant 
        """

        return self.session.get(QTable, id)
    
    def get_by_state(self, state):
        """
            Retourne les 4 ligne possible en fonction d'un état
        """

        return self.session.get(QTable, state)
    
    def update(self, gama, lr, action, state, new_q):

        q_table = self.session.query(QTable).filter(QTable.id == (gama, lr), QTable.state == state).first()
        if q_table:
            setattr(q_table, action, new_q)  # action = "action_up", "action_down", etc.
            self.session.commit()
        else:
            raise ValueError(f"QTable avec gama={gama}, lr={lr} introuvable.")