CDC_2026_MILESTONES = {
    12: {
        "age_label": "1 year",
        "source": "CDC Learn the Signs. Act Early. Milestones by 1 Year, Feb. 16, 2026",
        "social_emotional": [
            "Plays games with you, like pat-a-cake",
        ],
        "language_communication": [
            'Waves "bye-bye"',
            'Calls a parent "mama" or "dada" or another special name',
            'Understands "no" by pausing briefly or stopping',
        ],
        "cognitive": [
            "Puts something in a container, like a block in a cup",
            "Looks for things they see you hide, like a toy under a blanket",
        ],
        "movement_physical": [
            "Pulls up to stand",
            "Walks while holding on to furniture",
            "Drinks from a cup without a lid as you hold it",
            "Picks things up between thumb and pointer finger",
        ],
    },
    15: {
        "age_label": "15 months",
        "source": "CDC Learn the Signs. Act Early. Milestones by 15 Months, Feb. 16, 2026",
        "social_emotional": [
            "Copies other children while playing",
            "Shows you an object they like",
            "Claps when excited",
            "Hugs a stuffed doll or other toy",
            "Shows affection with hugs, cuddles, or kisses",
        ],
        "language_communication": [
            'Tries to say one or two words besides "mama" or "dada"',
            "Looks at a familiar object when you name it",
            "Follows directions given with both a gesture and words",
            "Points to ask for something or to get help",
        ],
        "cognitive": [
            "Tries to use things the right way, like a phone, cup, or book",
            "Stacks at least two small objects, like blocks",
        ],
        "movement_physical": [
            "Takes a few steps on their own",
            "Uses fingers to feed themself some food",
        ],
    },
    18: {
        "age_label": "18 months",
        "source": "CDC Learn the Signs. Act Early. Milestones by 18 Months, Feb. 16, 2026",
        "social_emotional": [
            "Moves away from you, but looks to make sure you are close by",
            "Points to show you something interesting",
            "Puts hands out for you to wash them",
            "Looks at a few pages in a book with you",
            "Helps you dress them by pushing an arm through a sleeve or lifting a foot",
        ],
        "language_communication": [
            'Tries to say three or more words besides "mama" or "dada"',
            'Follows one-step directions without gestures, like "Give it to me"',
        ],
        "cognitive": [
            "Copies you doing chores, like sweeping with a broom",
            "Plays with toys in a simple way, like pushing a toy car",
        ],
        "movement_physical": [
            "Walks without holding on to anyone or anything",
            "Scribbles",
            "Drinks from a cup without a lid and may spill sometimes",
            "Feeds themself with fingers",
            "Tries to use a spoon",
            "Climbs on and off a couch or chair without help",
        ],
    },
    24: {
        "age_label": "2 years",
        "source": "CDC Learn the Signs. Act Early. Milestones by 2 Years, Feb. 16, 2026",
        "social_emotional": [
            "Notices when others are hurt or upset",
            "Looks at your face to see how to react in a new situation",
        ],
        "language_communication": [
            'Points to things in a book when asked, like "Where is the bear?"',
            'Says at least two words together, like "More milk"',
            "Points to at least two body parts when asked",
            "Uses more gestures than waving and pointing",
        ],
        "cognitive": [
            "Holds something in one hand while using the other hand",
            "Tries to use switches, knobs, or buttons on a toy",
            "Plays with more than one toy at the same time",
        ],
        "movement_physical": [
            "Kicks a ball",
            "Runs",
            "Walks up a few stairs with or without help",
            "Eats with a spoon",
        ],
    },
}


def get_relevant_cdc_milestones(age_months):
    """Return the next CDC checkpoint for a child between 12 and 24 months."""
    if age_months < 12 or age_months > 24:
        return None

    for checkpoint_month in sorted(CDC_2026_MILESTONES):
        if age_months <= checkpoint_month:
            return checkpoint_month, CDC_2026_MILESTONES[checkpoint_month]

    return 24, CDC_2026_MILESTONES[24]


def format_milestones_for_prompt(age_months):
    milestone_match = get_relevant_cdc_milestones(age_months)
    if not milestone_match:
        return (
            "No CDC 2026 milestone checkpoint is available in the local dataset "
            f"for {age_months} months. Use general developmental guidance."
        )

    checkpoint_month, milestones = milestone_match
    sections = [
        ("Social/emotional", milestones["social_emotional"]),
        ("Language/communication", milestones["language_communication"]),
        ("Cognitive", milestones["cognitive"]),
        ("Movement/physical", milestones["movement_physical"]),
    ]
    lines = [
        f"Relevant CDC 2026 checkpoint: {milestones['age_label']} ({checkpoint_month} months).",
        f"Source: {milestones['source']}.",
        "CDC milestone context:",
    ]

    for section_name, section_milestones in sections:
        lines.append(f"- {section_name}: " + "; ".join(section_milestones))

    return "\n".join(lines)
