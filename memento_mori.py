"""
Memento Mori counter with many demographic adjustments.
"""
import sys
from datetime import datetime, timedelta
import tkinter as tk
import threading
import time
import argparse
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class Sex(Enum):
    MALE = auto()
    FEMALE = auto()
    INTERSEX = auto()


class Gender(Enum):
    MASC = auto()
    FEM = auto()
    NON_BINARY = auto()


class RelationshipStatus(Enum):
    SINGLE = auto()
    HAPPILY_MARRIED = auto()
    UNHAPPILY_MARRIED = auto()
    DIVORCED = auto()
    WIDOWED = auto()
    LONG_TERM_PARTNERSHIP = auto()
    POLYAMOROUS = auto()


@dataclass
class LifeExpectancyAdjustments:
    education: float = 0.0
    religious: float = 0.0
    income: float = 0.0
    relationship: float = 0.0
    gender_congruence: float = 0.0
    adhd: float = 0.0
    autism: float = 0.0
    left_handed: float = 0.0


def get_gender_adjustment(sex: Sex, gender: Gender) -> float:
    """
    Calculate life expectancy adjustment based on gender identity and sex assigned at birth.
    Values based on demographic studies of gender minority stress and health outcomes.
    """
    # Base adjustment for gender minority stress
    if gender == Gender.NON_BINARY:
        return -2.5  # Reflects impact of minority stress

    # Gender congruent with typical social expectations
    if (sex == Sex.MALE and gender == Gender.MASC) or (sex == Sex.FEMALE and gender == Gender.FEM):
        return 0.0  # No adjustment needed

    # Gender different from typical social expectations
    return -1.5  # Reflects impact of social pressure and minority stress


def get_relationship_adjustment(status: Optional[RelationshipStatus]) -> float:
    """
    Calculate life expectancy adjustment based on relationship status.
    Values based on demographic studies.
    """
    if status is None:
        return 0.0

    adjustments = {
        RelationshipStatus.SINGLE: -3.5,  # Moderate decrease
        RelationshipStatus.HAPPILY_MARRIED: 3.7,  # Significant increase
        RelationshipStatus.UNHAPPILY_MARRIED: -5.0,  # Substantial decrease
        RelationshipStatus.DIVORCED: -3.0,  # Similar to single but with additional stress
        RelationshipStatus.WIDOWED: -4.0,  # Significant impact from loss
        RelationshipStatus.LONG_TERM_PARTNERSHIP: 3.0,  # Similar to happy marriage
        RelationshipStatus.POLYAMOROUS: 1.5  # Limited data, estimated positive based on social support
    }
    return adjustments[status]


def get_conditional_life_expectancy(current_age: float, sex: Sex) -> float:
    """
    Returns the conditional life expectancy based on current age and sex.
    Using 2021 US Life Tables from CDC/NCHS.
    """
    # Life tables by sex
    life_tables: dict[Sex, dict[int, float]] = {
        Sex.MALE: {
            0: 76.1,
            15: 62.3,
            25: 52.7,
            35: 43.3,
            45: 34.2,
            50: 30.0,
            55: 26.0,
            65: 18.3,
            75: 11.7,
            85: 6.3
        },
        Sex.FEMALE: {
            0: 81.2,
            15: 67.3,
            25: 57.6,
            35: 47.9,
            45: 38.4,
            50: 33.9,
            55: 29.6,
            65: 21.1,
            75: 13.6,
            85: 7.2
        },
        Sex.INTERSEX: {  # Uses average of male and female as approximation
            0: 78.65,
            15: 64.8,
            25: 55.15,
            35: 45.6,
            45: 36.3,
            50: 31.95,
            55: 27.8,
            65: 19.7,
            75: 12.65,
            85: 6.75
        }
    }

    life_table = life_tables[sex]
    closest_age: int = max([age for age in life_table.keys() if age <= current_age])
    base_conditional: float = life_table[closest_age]
    years_since_closest: float = current_age - closest_age
    adjusted_conditional: float = base_conditional - years_since_closest

    return adjusted_conditional + closest_age


def calculate_remaining_time(
        birth_date: datetime,
        sex: Sex,
        gender: Gender,
        adjustments: LifeExpectancyAdjustments
) -> timedelta:
    """Calculate remaining days based on personal factors."""
    current_date: datetime = datetime.now()
    current_age: float = (current_date - birth_date).days / 365.25

    # Get base conditional life expectancy
    conditional_expectancy: float = get_conditional_life_expectancy(current_age, sex)

    # Apply adjustments
    total_adjustment: float = sum(vars(adjustments).values())
    adjusted_life_expectancy: float = conditional_expectancy + total_adjustment

    # Calculate remaining time
    death_date: datetime = birth_date + timedelta(days=adjusted_life_expectancy * 365.25)
    remaining: timedelta = death_date - current_date

    return remaining


class MementoMoriCounter:
    def __init__(
            self,
            birth_date: datetime,
            sex: Sex,
            gender: Gender,
            adjustments: LifeExpectancyAdjustments
    ):
        self.birth_date = birth_date
        self.sex = sex
        self.gender = gender
        self.adjustments = adjustments

        # Create the main window
        self.root: tk.Tk = tk.Tk()
        self.root.title("Memento Mori")

        # Set window properties
        self.root.attributes('-topmost', True)  # Keep window on top
        self.root.geometry("300x150")  # Set window size

        # Create labels
        self.days_label: tk.Label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 24),
            wraplength=280
        )
        self.days_label.pack(pady=20)

        self.update_label: tk.Label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 10),
            wraplength=280
        )
        self.update_label.pack(pady=10)

        # Start update thread
        self.running: bool = True
        self.update_thread: threading.Thread = threading.Thread(target=self.update_time)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Update display immediately
        self.update_display()

    def update_display(self) -> None:
        """Update the display with current remaining time."""
        remaining: timedelta = calculate_remaining_time(self.birth_date, self.sex, self.gender, self.adjustments)

        # Format the display text
        days: int = remaining.days
        hours: int = remaining.seconds // 3600

        self.days_label.config(
            text=f"{days:,} days\n{hours} hours"
        )

        current_time: str = datetime.now().strftime("%H:%M:%S")
        self.update_label.config(
            text=f"Last updated: {current_time}"
        )

    def update_time(self) -> None:
        """Update the display every hour."""
        while self.running:
            self.update_display()
            # Sleep until the start of the next hour
            now: datetime = datetime.now()
            next_hour: datetime = (now + timedelta(hours=1)).replace(
                minute=0, second=0, microsecond=0
            )
            sleep_seconds: float = (next_hour - now).total_seconds()
            time.sleep(sleep_seconds)

    def on_closing(self) -> None:
        """Clean up when the window is closed."""
        self.running = False
        self.root.destroy()

    def run(self) -> None:
        """Start the application."""
        self.root.mainloop()



def parse_arguments() -> tuple[datetime, Sex, Gender, LifeExpectancyAdjustments]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=('Display a Memento Mori counter showing remaining days of life.'
        'WARNING: the values came from an LLM and have not been checked.')
    )

    # Required arguments
    parser.add_argument(
        'birth_date',
        help='Your birth date in YYYY-MM-DD format'
    )
    parser.add_argument(
        '--sex',
        choices=['male', 'female', 'intersex'],
        required=True,
        help='Sex assigned at birth (note: intersex calculations are a wild guess)'
    )
    parser.add_argument(
        '--gender',
        choices=['masc', 'fem', 'non-binary'],
        required=True,
        help='Gender presentation/identity'
    )

    # Relationship status (mutually exclusive)
    relationship_group = parser.add_mutually_exclusive_group()
    relationship_group.add_argument(
        '--single',
        action='store_true',
        help='Single status (-3.5 years)'
    )
    relationship_group.add_argument(
        '--happily-married',
        action='store_true',
        help='Happily married (+3.7 years)'
    )
    relationship_group.add_argument(
        '--unhappily-married',
        action='store_true',
        help='Unhappily married (-5.0 years)'
    )
    relationship_group.add_argument(
        '--divorced',
        action='store_true',
        help='Divorced (-3.0 years)'
    )
    relationship_group.add_argument(
        '--widowed',
        action='store_true',
        help='Widowed (-4.0 years)'
    )
    relationship_group.add_argument(
        '--long-term-partnership',
        action='store_true',
        help='Long-term partnership (+3.0 years)'
    )
    relationship_group.add_argument(
        '--polyamorous',
        action='store_true',
        help='Polyamorous relationships (+1.5 years)'
    )

    parser.add_argument(
        '--college-educated',
        action='store_true',
        help='College education (+4.5 years)'
    )
    parser.add_argument(
        '--religious',
        action='store_true',
        help='Regular religious attendance (+5.0 years)'
    )
    parser.add_argument(
        '--high-income',
        action='store_true',
        help='Income >1 SD above mean (+2.5 years)'
    )
    parser.add_argument(
        '--adhd',
        action='store_true',
        help='ADHD diagnosis (-3.0 years)'
    )
    parser.add_argument(
        '--autism',
        action='store_true',
        help='Autism diagnosis (-2.0 years)'
    )
    parser.add_argument(
        '--left-handed',
        action='store_true',
        help='Left-handedness (-1.0 years)'
    )

    args = parser.parse_args()

    # Parse birthdate
    try:
        birth_date = datetime.strptime(args.birth_date, '%Y-%m-%d')
    except ValueError:
        parser.error('Birth date must be in YYYY-MM-DD format')
        sys.exit()  # Unreachable. Here to help the IDE.

    # Convert sex and gender strings to enums
    sex_map = {'male': Sex.MALE, 'female': Sex.FEMALE, 'intersex': Sex.INTERSEX}
    gender_map = {'masc': Gender.MASC, 'fem': Gender.FEM, 'non-binary': Gender.NON_BINARY}

    sex = sex_map[args.sex]
    gender = gender_map[args.gender]

    # Determine relationship status
    relationship_status = None
    if args.single:
        relationship_status = RelationshipStatus.SINGLE
    elif args.happily_married:
        relationship_status = RelationshipStatus.HAPPILY_MARRIED
    elif args.unhappily_married:
        relationship_status = RelationshipStatus.UNHAPPILY_MARRIED
    elif args.divorced:
        relationship_status = RelationshipStatus.DIVORCED
    elif args.widowed:
        relationship_status = RelationshipStatus.WIDOWED
    elif args.long_term_partnership:
        relationship_status = RelationshipStatus.LONG_TERM_PARTNERSHIP
    elif args.polyamorous:
        relationship_status = RelationshipStatus.POLYAMOROUS

    # Create adjustments based on flags
    adjustments = LifeExpectancyAdjustments(
        education=4.5 if args.college_educated else 0.0,
        religious=5.0 if args.religious else 0.0,
        income=2.5 if args.high_income else 0.0,
        relationship=get_relationship_adjustment(relationship_status),
        gender_congruence=get_gender_adjustment(sex, gender),
        adhd=-3.0 if args.adhd else 0.0,
        autism=-2.0 if args.autism else 0.0,
        left_handed=-1.0 if args.left_handed else 0.0
    )

    return birth_date, sex, gender, adjustments


if __name__ == "__main__":
    app = MementoMoriCounter(*parse_arguments())
    app.run()
