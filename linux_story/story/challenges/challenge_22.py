#!/usr/bin/env python
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# A chapter of the story

from linux_story.Step import Step
from linux_story.step_helper_functions import unblock_commands_with_cd_hint
from linux_story.story.terminals.terminal_mkdir import TerminalMkdir
from linux_story.helper_functions import play_sound
from linux_story.story.challenges.challenge_23 import Step1 as NextChallengeStep


class StepTemplateMkdir(Step):
    challenge_number = 22

    def __init__(self, xp=''):
        Step.__init__(self, TerminalMkdir, xp)


class Step1(StepTemplateMkdir):
    story = [
        "{{gb:Well done, it looks like everyone is here!}}"
        "\nRuth: {{Bb:Thank you so much! "
        "We'll stay in here to keep safe.  I'm so grateful to everything "
        "you've done}}",
        "\nUse {{yb:cat}} to check that everyone is happy in here."
    ]

    start_dir = "~/farm/barn/.shelter"
    end_dir = "~/farm/barn/.shelter"
    commands = [
        "cat Daisy",
        "cat Trotter",
        "cat Cobweb"
    ]

    def next(self):
        play_sound("bell")
        Step2()


class Step2(StepTemplateMkdir):
    def __init__(self):
        "Ruth: {{Bb:What?? I heard a bell!  What does that mean?}}",
        "\nQuick! Look around and see if anyone is missing"

    start_dir = "~/farm/barn/.shelter"
    end_dir = "~/farm/barn/.shelter"
    commands = [
        "ls",
        "ls -a"
    ]
    hints = [
        "{{rb:Look around with}} {{yb:ls}}"
    ]

    def next(self):
        play_sound("bell")
        Step3()


class Step3(StepTemplateMkdir):

    def __init__(self):
        "Ruth: {{Bb:I heard it again!  Is that the sound you heard when "
        "my husband went missing?}}",
        "Have another quick look around"

    start_dir = "~/farm/barn/.shelter"
    end_dir = "~/farm/barn/.shelter"
    commands = [
        "ls",
        "ls -a"
    ]
    hints = [
        "{{rb:Look around with}} {{yb:ls}}"
    ]

    def next(self):
        Step4()


class Step4(StepTemplateMkdir):
    story = [
        "Ruth: {{Bb:It's alright. We're all safe, everyone's still here. "
        "I wonder why it's ringing?}}"
        "\nPerhaps we should investigate that sound.  Who else could do we know?",
        "Maybe you could check back on the family in the {{yb:.hidden-shelter}} ",
        "and see if you can talk with your new found voice.",
        "Start heading back to the {{yb:.hidden-shelter}} using {{yb:cd}}"
    ]

    start_dir = "~/farm/barn/.shelter"
    end_dir = "~/town/.hidden-shelter"
    commands = [
        "cd ~/town/.hidden-shelter"
    ]
    hints = [
        "{{rb:We can go directly to the}} {{yb:.hidden-shelter}} "
        "{{rb:using}} {{yb:cd ~/town/.hidden-shelter}}"
    ]

    def block_command(self, line):
        return unblock_commands_with_cd_hint(line, self.commands)

    def next(self):
        Step5()


class Step5(StepTemplateMkdir):
    story = [
        "Have a look around."
    ]

    start_dir = "~/town/.hidden-shelter",
    end_dir = "~/town/.hidden-shelter"
    commands = [
        "ls",
        "ls -a"
    ]
    hints = [
        "{{rb:Use}} {{yb:ls}} {{rb:to look around.}}"
    ]
    last_step = True

    def next(self):
            NextChallengeStep(self.xp)