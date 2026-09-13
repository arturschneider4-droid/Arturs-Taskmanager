from taskmanager.v8_interactions import install_drop_guard, drop_event_was_accepted
from taskmanager.ui import DropList


class FakeDropEvent:
    def __init__(self, accepted):
        self.accepted = accepted

    def isAccepted(self):
        return self.accepted


def test_rejected_drop_is_not_a_move():
    assert drop_event_was_accepted(FakeDropEvent(False)) is False


def test_accepted_drop_is_a_move():
    assert drop_event_was_accepted(FakeDropEvent(True)) is True


def test_v8_installs_the_guard_once():
    install_drop_guard(object())
    assert DropList._v8_drop_guard_installed is True
