from enum import Enum

class VoteTypeEnum(Enum):
    LegislationConstitution = 0
    LegislationLaw          = 1
    LegislationAffair       = 2
    Justice                 = 3
    ElectionJudge           = 4
    ElectionAdmin           = 5
    ElectionWardenry        = 6
    Impeachment             = 7
    Invite                  = 8


class PunishmentTypeEnum(Enum):
    Jailed                  = 0
    Kicked                  = 1
    Disfranchise            = 2
