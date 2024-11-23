# Overview
This is a quick program I created to run on boot-up. It calculates a more nuanced life expectancy than
I got from just using the mean life expectancy.

**WARNING**
*Most of this code (and the figures) came from Claude 3.5 Sonnet. There will be hallucinations.
This is fine for my purposes, but might not be for yours.*

Even if the figures are correct (they aren't), the
calculation method does not deal with interactions
between factors. For example, a widowed heterosexual 
male lives less time than a similar female. But this
code just treats "widowed" as a single factor. It also
does not represent happily married widows or many other
situations.

# Running

You'll need a copy of Python version 3 or later
installed to run this program. If you're on Windows,
I recommend `scoop`. Use `scoop install python` once
you've got `scoop` installed.

Pass `--help` to the program to see its options. Here
is an example usage giving a *memento mori* for a 9/11
baby who is a member of a lot of minority groups.

```sh
python memento_mori.py 2001-09-11 --sex female --gender non-binary --long-term-partnership --college-educated -
-religious --high-income --adhd --autism --left-handed
```

# Running on startup

On Windows (maybe I'll get around to Mac and Linux someday.)

1. Start Windows Task Scheduler (Win+R then type "taskschd.msc")
2. Click "Create Basic Task" in the far right listbox titled "Actions"
3. Choose the options you want (e.g., Run when I log on)
4. After you've chosen "Start a Program",
   * Program is "pythonw" (this keeps it from showing the console window)
   * Arguments are everything else in the command line
   * You'll need to give a full path to the memento_mori.py file
