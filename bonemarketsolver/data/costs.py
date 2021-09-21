__all__ = ['Cost']
__author__ = "Jeremy Saklad"

from enum import Enum

from ortools.sat.python import cp_model

class Cost(Enum):
    """The number of pennies needed to produce a quality."""

    __slots__ = '_value_', '_name_', '__objclass__'

    # This is your baseline EPA: the pennies you could generate using an action for a generic grind.
    ACTION = 400

    # Antique Mystery
    ANTIQUE_MYSTERY = 1250

    # Favours: Bohemians
    # Various opportunity cards
    BOHEMIAN_FAVOURS = ACTION

    # Bone Fragment
    BONE_FRAGMENT = 1

    # Cartographer's Hoard
    CARTOGRAPHERS_HOARD = 31250

    # Favours: The Church
    # Various opportunity cards
    CHURCH_FAVOURS = ACTION

    # Collection Note: There's a 'Package' in London
    # Station VIII Lab
    COLLECTION_NOTE = ACTION

    # Deep-Zee Catch
    # Spear-fishing at the bottom of the Evenlode, 7 at a time, difficult check, available fourth of the time
    DEEP_ZEE_CATCH = 4*(ACTION/7)

    # Crustacean Pincer
    # Ealing Gardens Butcher, 2 at a time
    CRUSTACEAN_PINCER = (ACTION + DEEP_ZEE_CATCH)/2

    # Femur of a Surface Deer
    # Dumbwaiter of Balmoral, 25 at a time
    DEER_FEMUR = ACTION/25

    # Favours: The Docks
    # Various opportunity cards
    DOCK_FAVOURS = ACTION

    # Extraordinary Implication
    EXTRAORDINARY_IMPLICATION = 250

    # Eyeless Skull
    # No consistent source
    EYELESS_SKULL = cp_model.INT32_MAX/2

    # Holy Relic of the Thigh of Saint Fiacre
    # Jericho Locks statue, 2 at a time
    FIACRE_THIGH = (ACTION + 4*CHURCH_FAVOURS)/2

    # Fin Bones, Collected
    # Hunt and dissect Pinewood Shark, 40 at a time
    FIN_BONES = (11*ACTION)/40

    # Amber-Crusted Fin
    # Helicon House
    AMBER_FIN = ACTION + 10*FIN_BONES

    # Five-Pointed Ribcage
    # Upwards
    FIVE_POINTED_RIBCAGE = 9*ACTION + CARTOGRAPHERS_HOARD

    # Esteem of the Guild
    # Jericho Parade, 2 at a time
    GUILD_ESTEEM = (ACTION + 5*DOCK_FAVOURS)/2

    # Skull in Coral
    # Persephone, 1-2 at a time
    CORAL_SKULL = 1.5*(2*ACTION + 3*GUILD_ESTEEM)

    # Headless Skeleton
    # These are accumulated while acquiring other qualities.
    HEADLESS_SKELETON = 0

    # Favours: Hell
    # Various opportunity cards
    HELL_FAVOURS = ACTION

    # Infiltrating...
    # Khan's Heart, 10 at a time
    INFILTRATING = ACTION/10

    # Intercepted Cablegram
    # Khan's Heart, tap a telegraph cable, 50 at a time
    INTERCEPTED_CABLEGRAM = (2*ACTION + 130*INFILTRATING)/50

    # Volume of Collated Research
    # Hurlers statue, 10 at a time
    COLLATED_RESEARCH = (ACTION + 4*HELL_FAVOURS)/10

    # Hinterland Scrip
    HINTERLAND_SCRIP = 50

    # Fossilised Forelimb
    # Anning and Daughters
    FOSSILISED_FORELIMB = 55*HINTERLAND_SCRIP

    # Hedonist
    # Handsome Townhouse, 3cp at a time
    HEDONIST_CP = ACTION/3

    # Human Arm
    # These are accumulated while acquiring other qualities.
    HUMAN_ARM = 0

    # Incisive Observation
    INCISIVE_OBSERVATION = 50

    # Crate of Incorruptible Biscuits
    INCORRUPTIBLE_BISCUITS = 250

    # Inkling of Identity
    INKLING_OF_IDENTITY = 10

    # A Custom-Engraved Skull
    # Feast of the Exceptional Rose, sent by one player and accepted by another
    ENGRAVED_SKULL = 2*ACTION + 200*INKLING_OF_IDENTITY

    # Ivory Humerus
    # Ealing Gardens statue, 2 at a time
    IVORY_HUMERUS = (ACTION + 4*BOHEMIAN_FAVOURS)/2

    # Jade Fragment
    JADE_FRAGMENT = 1

    # Femur of a Jurassic Beast
    # Brawling for yourself, large Bone Market crate, 12 at a time
    JURASSIC_FEMUR = (10*ACTION)/12

    # Knotted Humerus
    # These are accumulated while acquiring other qualities.
    KNOTTED_HUMERUS = 0

    # Nevercold Brass Sliver
    NEVERCOLD_BRASS = 1

    # Obsidian Chitin Tail
    # No consistent source
    OBSIDIAN_TAIL = cp_model.INT32_MAX/2

    # Parabolan Orange-apple
    # Parabolan Base-camp, electricity and hedonism, 2 at a time
    ORANGE_APPLE = (2*ACTION + 100*BONE_FRAGMENT + 21*HEDONIST_CP)/2

    # Ivory Femur
    # Bohemian Sculptress
    IVORY_FEMUR = ACTION + 750*BONE_FRAGMENT + 3*ORANGE_APPLE

    # Penny
    PENNY = 1

    # Bright Brass Skull
    # Merrigans Exchange
    BRASS_SKULL = 6250*PENNY

    # Pentagrammic Skull
    # Upwards
    PENTAGRAMMIC_SKULL = 9*ACTION

    # Hand-picked Peppercaps
    PEPPERCAPS = HINTERLAND_SCRIP

    # Revisionist Historical Narrative
    # Waswood
    REVISIONIST_NARRATIVE = ACTION + 4*EXTRAORDINARY_IMPLICATION + INCISIVE_OBSERVATION

    # Knob of Scintillack
    SCINTILLACK = 250

    # Searing Enigma
    # Khan's Heart, disgruntled academic
    SEARING_ENIGMA = 2*ACTION + 130*INFILTRATING + 2*INTERCEPTED_CABLEGRAM

    # Carved Ball of Stygian Ivory
    STYGIAN_IVORY = 250

    # Preserved Surface Blooms
    SURFACE_BLOOMS = 250

    # Consignment of Scintillack Snuff
    # Laboratory Manufacturing
    SCINTILLACK_SNUFF = (ACTION + 8*SCINTILLACK + SURFACE_BLOOMS)/2

    # Elation at Feline Oration
    # Pinnock
    ELATION_AT_FELINE_ORATION = ACTION + 2*ANTIQUE_MYSTERY + COLLECTION_NOTE + 2*SCINTILLACK_SNUFF

    # Oil of Companionship
    # Station VIII Lab
    OIL_OF_COMPANIONSHIP = ACTION + ELATION_AT_FELINE_ORATION

    # Survey of the Neath's Bones
    # Laboratory Research
    SURVEY = 6*ACTION/25

    # Plaster Tail Bones
    # Carpenter's Granddaughter, 2 at a time
    PLASTER_TAIL_BONES = (ACTION + 10*SURVEY)/2

    # Human Ribcage
    # Ealing Gardens
    HUMAN_RIBCAGE = ACTION + 15*SURVEY

    # Palaeontological Discovery
    # Plain of Thirsty Grasses
    PALAEONTOLOGICAL_DISCOVERY = (ACTION + 140*SURVEY)/6

    # Helical Thighbone
    # Results of Excavation, 6 at a time
    HELICAL_THIGH = (2*PALAEONTOLOGICAL_DISCOVERY)/6

    # Leviathan Frame
    # Results of Excavation
    LEVIATHAN_FRAME = 25*PALAEONTOLOGICAL_DISCOVERY

    # Thorned Ribcage
    # Iron-Toothed Terror Bird
    THORNED_RIBCAGE = 6*ACTION

    # Flourishing Ribcage
    # Helicon House
    FLOURISHING_RIBCAGE = ACTION + HUMAN_RIBCAGE + THORNED_RIBCAGE

    # Time Remaining in the Woods
    # Compel Ghillie, 7 at a time
    TIME_REMAINING_IN_THE_WOODS = (ACTION + 4*COLLATED_RESEARCH)/7

    # Observation: Red Deer
    # Balmoral Woods (TRitW rounded up to multiple of 7)
    DEER_OBSERVATION = 13*ACTION + 14*TIME_REMAINING_IN_THE_WOODS

    # Mammoth Ribcage
    # Keeper of the Marigold Menagerie
    MAMMOTH_RIBCAGE = ACTION + DEER_OBSERVATION

    # Observation: Fox
    # Balmoral Woods (TRitW rounded up to multiple of 7)
    FOX_OBSERVATION = 10*ACTION + 14*TIME_REMAINING_IN_THE_WOODS

    # Doubled Skull
    # Keeper of the Marigold Menagerie
    DOUBLED_SKULL = ACTION + FOX_OBSERVATION

    # Observation: Grouse
    # Balmoral Woods (TRitW rounded up to multiple of 7)
    GROUSE_OBSERVATION = 9*ACTION + 14*TIME_REMAINING_IN_THE_WOODS

    # Skeleton with Seven Necks
    # Keeper of the Marigold Menagerie
    SKELETON_WITH_SEVEN_NECKS = ACTION + GROUSE_OBSERVATION

    # Rubbery Skull
    # Flute Street, including travel due to quality cap
    RUBBERY_SKULL = 25*ACTION

    # Rumour of the Upper River
    RUMOUR_OF_THE_UPPER_RIVER = 250

    # Jet Black Stinger
    # Hunting with Sophia's, 5 at a time
    BLACK_STINGER = (ACTION + 5*RUMOUR_OF_THE_UPPER_RIVER)/5

    # Prismatic Frame
    # Expedition at Station VIII
    PRISMATIC_FRAME = ACTION + OIL_OF_COMPANIONSHIP + 98*RUMOUR_OF_THE_UPPER_RIVER

    # Unidentified Thigh Bone
    # These are accumulated while acquiring other qualities.
    UNIDENTIFIED_THIGH = 0

    # Nodule of Warm Amber
    WARM_AMBER = 10

    # Albatross Wing
    # Ealing Gardens Butcher, 2 at a time
    ALBATROSS_WING = (ACTION + 2000*BONE_FRAGMENT + 25*WARM_AMBER)/2

    # Bat Wing
    # Ealing Gardens Butcher, 2 at a time
    BAT_WING = (ACTION + 100*BONE_FRAGMENT + 2*WARM_AMBER)/2

    # Horned Skull
    # Ealing Gardens Butcher
    HORNED_SKULL = ACTION + 1000*BONE_FRAGMENT + 5*WARM_AMBER

    # Plated Skull
    # Ealing Gardens Butcher
    PLATED_SKULL = ACTION + 1750*BONE_FRAGMENT + INCORRUPTIBLE_BISCUITS + 25*WARM_AMBER

    # Sabre-toothed Skull
    # Ealing Gardens Butcher
    SABRE_TOOTHED_SKULL = ACTION + 4900*BONE_FRAGMENT + 125*WARM_AMBER

    # Wing of a Young Terror Bird
    # Ealing Gardens Butcher, 2 at a time
    TERROR_BIRD_WING = (ACTION + 100*BONE_FRAGMENT + 25*WARM_AMBER)/2

    # Tomb-Lion's Tail
    # Ealing Gardens Butcher
    TOMB_LION_TAIL = ACTION + 200*BONE_FRAGMENT + 2*WARM_AMBER

    # Nodule of Trembling Amber
    # Slime and Amber: the Rubbery Men (minus 1 action to account for Favour)
    TREMBLING_AMBER = 100*WARM_AMBER

    # Ribcage with a Bouquet of Eight Spines
    # Helicon House
    RIBCAGE_WITH_EIGHT_SPINES = ACTION + 3*SEARING_ENIGMA + SKELETON_WITH_SEVEN_NECKS + THORNED_RIBCAGE + 3*TREMBLING_AMBER

    # Withered Tentacle
    # Adulterine Castle, Miscounting Second Circle by 4, 4 at a time
    WITHERED_TENTACLE = ACTION/4


