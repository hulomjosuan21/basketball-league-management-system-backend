from src.extensions import db
from src.utils.db_utils import UUIDGenerator, CreatedAt

class PaymentModel(db.Model):
    __tablename__ = 'payments_table'

    payment_id = UUIDGenerator(db, 'payment')
    payer_team_id = db.Column(db.String, db.ForeignKey('teams_table.team_id', ondelete="SET NULL"), nullable=True)
    league_id = db.Column(db.String, db.ForeignKey('leagues_table.league_id', ondelete="CASCADE"), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    reference_number = db.Column(db.String(250), nullable=True)
    status = db.Column(db.Enum('Pending', 'Paid', 'Failed', 'Refunded', name='payment_status'), nullable=False, default='Pending')

    paid_at = CreatedAt(db)

    team = db.relationship('TeamModel', back_populates='payments')
    league = db.relationship('LeagueModel', back_populates='payments')

    def to_json(self):
        return {
            "payment_id": self.payment_id,
            "team_id": self.payer_team_id,
            "league_id": self.league_id,
            "amount": self.amount,
            "reference_number": self.reference_number,
            "status": self.status,
            "paid_at": self.paid_at.isoformat()
        }
