from enum import Enum

class VoteTypeEnum(Enum):
    LegislationConstitution = 0
    LegislationLaw          = 1
    LegislationAffair       = 2
    Justice                 = 3
    ElectionJudge           = 4
    ElectionAdmin           = 5
    ElectionWardenry        = 6
    ElectionTechnical       = 7
    ElectionPropaganda      = 8
    Impeachment             = 9
    Invite                  = 10


class PunishmentTypeEnum(Enum):
    Jailed                  = 0
    Kicked                  = 1
    Disfranchise            = 2


class CaseStepEnum(Enum):
    First                   = 0
    Second                  = 1


class CaseWinnerEnum(Enum):
    Appeallees              = 0
    Appeallors              = 1
    NotDetermined           = 2


class PunishmentAuthorityEnum(Enum):
    Admin                   = 0
    Public                  = 1


class UIVotingButtonEnum(Enum):
    Agree                   = "Agree"
    Waiver                  = "Waiver"
    Against                 = "Against"


class UIQuestionDifficultyEnum(Enum):
    Easy                    = "Easy"
    Hard                    = "Hard"
