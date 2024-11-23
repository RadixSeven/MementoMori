from datetime import datetime, timedelta
import tkinter as tk
import threading
import time
import argparse
from dataclasses import dataclass


@dataclass
class LifeExpectancyAdjustments:
    education: float
    religious: float
    income: float
    marital: float
    adhd: float
    autism: float
    left_handed: float


def get_conditional_life_expectancy(current_age: float) -> float:
    """
    Returns the conditional life expectancy based on current age.
    Using 2021 US Life Tables from CDC/NCHS.
    """
    male_life_table: dict[int, float] = {
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
    }

    closest_age: int = max([age for age in male_life_table.keys() if age <= current_age])
    base_conditional: float = male_life_table[closest_age]
    years_since_closest: float = current_age - closest_age
    adjusted_conditional: float = base_conditional - years_since_closest

    return adjusted_conditional + closest_age


def calculate_remaining_time(birth_date: datetime) -> timedelta:
    """Calculate remaining days based on personal factors."""
    current_date: datetime = datetime.now()
    current_age: float = (current_date - birth_date).days / 365.25

    # Personal adjustments
    adjustments: LifeExpectancyAdjustments = LifeExpectancyAdjustments(
        education=4.5,  # College education
        religious=5.0,  # Frequent religious attendance
        income=2.5,  # >1 SD above mean
        marital=-5.0,  # Unhappy marriage
        adhd=-3.0,  # ADHD diagnosis
        autism=-2.0,  # Autism diagnosis
        left_handed=-1.0  # Left-handedness
    )

    # Get base conditional life expectancy
    conditional_expectancy: float = get_conditional_life_expectancy(current_age)

    # Apply adjustments
    total_adjustment: float = sum(vars(adjustments).values())
    adjusted_life_expectancy: float = conditional_expectancy + total_adjustment

    # Calculate remaining time
    death_date: datetime = birth_date + timedelta(days=adjusted_life_expectancy * 365.25)
    remaining: timedelta = death_date - current_date

    return remaining


class MementoMoriCounter:
    def __init__(self, birth_date: datetime):
        # Create the main window
        self.root: tk.Tk = tk.Tk()
        self.root.title("Memento Mori")

        # Set window properties
        self.root.attributes('-topmost', True)  # Keep window on top
        self.root.geometry("300x150")  # Set window size

        self.birth_date: datetime = birth_date

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
        remaining: timedelta = calculate_remaining_time(self.birth_date)

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


def parse_birth_date() -> datetime:
    """Parse birthdate from command line arguments."""
    parser = argparse.ArgumentParser(
        description='Display a Memento Mori counter showing remaining days of life.'
    )
    parser.add_argument(
        'birth_date',
        help='Your birth date in YYYY-MM-DD format'
    )
    args = parser.parse_args()

    try:
        return datetime.strptime(args.birth_date, '%Y-%m-%d')
    except ValueError:
        parser.error('Birth date must be in YYYY-MM-DD format')


if __name__ == "__main__":
    app = MementoMoriCounter(parse_birth_date())
    app.run()