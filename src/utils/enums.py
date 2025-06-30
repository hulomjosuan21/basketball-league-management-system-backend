from enum import Enum
class NotificationAction(str, Enum):
    PLAYER_INVITATION = 'player_invitation'

    @staticmethod
    def from_value(value: str):
        for action in NotificationAction:
            if action.value == value:
                return action
        return None