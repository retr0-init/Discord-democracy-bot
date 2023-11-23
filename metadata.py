from typing import Dict, List

ROLE_ID_LIST: Dict[str, int] = {
    "Admin":        0,
    "Judge":        0,
    "Wardenry":     0,
    "Propaganda":   0,
    "Technical":    0,
    "Left":         0,
    "Right":        0,
    "Anarchy":      0,
    "Extreme":      0,
    "Mild":         0,
    "Temp":         0,
    "Citizen":      0,
    "Defendant":    0,
    "Accuser":      0,
    "Prisoner":     0,
    "Lawyer":       0
}
ROLE_ROLE_LIST: Dict[str, List[str]] = {
    "Official":     [
        "Admin",
        "Judge",
        "Wardenry",
        "Propaganda",
        "Technical"
    ],
    "Electorate":   [
        "Left",
        "Right",
        "Anarchy",
        "Extreme",
        "Mild"
    ],
    "Identity":     [
        "Temp",
        "Citizen",
        "Prisoner",
        "Defendant",
        "Accuser",
        "Lawyer"
    ]
}
CHANNEL_ID_LIST: Dict[str, int] = {
    "Jail":         0,
    "Court":        0,
    "Invite":       0,
    "Election":     0,
    "Publish":      0
}
