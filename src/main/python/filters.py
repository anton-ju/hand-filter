import operator
import logging
from utils import load_ps_notes

logger = logging.getLogger(__name__)


class Condition:
    def __init__(self, attr, op, value):
        self.attr = attr
        self.value = value
        self.operator = op

    def __call__(self, parsed_hand, **kwargs):
        try:
            attr = getattr(parsed_hand, self.attr)
        except AttributeError as e:
            logger.exception(e)
            return False

        return self.operator(attr, self.value)


class HandFilter:
    def __init__(self):
        self.conditions = []

    def clear(self):
        self.conditions.clear()

    def add_condition(self, func, **kwargs):
        """Filter function should accept parsed hh and return Bool"""
        self.conditions.append((func, kwargs))

    def check_conditions(self, parsed_hand, **kwargs_new):
        pass_conditions = []
        for func, kwargs in self.conditions:
            kwargs.update(kwargs_new)
            result = func(parsed_hand, **kwargs)
            pass_conditions.append(result)

        return all(pass_conditions)


"""Custom filters
"""

class CORegFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'CO' and notes.get(player, 'uu') in config['REG_LABELS']:
                return True
        return False


class BURegFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'BU' and notes.get(player, 'uu') in config['REG_LABELS']:
                return True
        return False


class SBRegFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'SB' and notes.get(player, 'uu') in config['REG_LABELS']:
                return True
        return False


class BBRegFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'BB' and notes.get(player, 'uu') in config['REG_LABELS']:
                return True
        return False


class BBFishFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'BB' and notes.get(player, 'uu') in config['FISH_LABELS']:
                return True
        return False


class SBFishFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'SB' and notes.get(player, 'uu') in config['FISH_LABELS']:
                return True
        return False


class BUFishFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'BU' and notes.get(player, 'uu') in config['FISH_LABELS']:
                return True
        return False


class COFishFilter:
    def __call__(self, hh, **kwargs):
        notes = kwargs.get('notes')
        config = kwargs.get('config')
        for player, pos in hh.positions.items():
            if pos == 'CO' and notes.get(player, 'uu') in config['FISH_LABELS']:
                return True
        return False


class BUCoversSBBB:
    """Filter returns true if BU chips amount greater then SB and BB chips"""
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('BU', 0) >= chips.get('SB', 0)) and (chips.get('BU', 0) >= chips.get('BB', 0)):
            return True
        else:
            return False


class BUNotCoversSBBB:
    """Filter returns true if BU chips amount less then SB and BB chips"""
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('BU', 0) < chips.get('SB', 0)) and (chips.get('BU', 0) < chips.get('BB', 0)):
            return True
        else:
            return False


class BUCoversSBNotBB:
    """Filter returns true if BU chips amount greater then SB and less then BB chips"""
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('BU', 0) >= chips.get('SB', 0)) and (chips.get('BU', 0) < chips.get('BB', 0)):
            return True
        else:
            return False


class BUCoversBBNotSB:
    """Filter returns true if BU chips amount greater then BB and less then SB chips"""
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('BU', 0) >= chips.get('BB', 0)) and (chips.get('BU', 0) < chips.get('SB', 0)):
            return True
        else:
            return False


class COCoversBUSBBB:
    """Filter returns true if CO chips amount greater then BU, SB and BB chips"""
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if ( chips.get('CO', 0) >= chips.get('BU', 0)) and \
                (chips.get('CO', 0) >= chips.get('SB', 0)) and \
                (chips.get('CO', 0) >= chips.get('BB', 0)):
            return True
        else:
            return False


class CONotCoversBUSBBB:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if ( chips.get('CO', 0) < chips.get('BU', 0)) and \
                (chips.get('CO', 0) < chips.get('SB', 0)) and \
                (chips.get('CO', 0) < chips.get('BB', 0)):
            return True
        else:
            return False


class COCoversBU:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('CO', 0) >= chips.get('BU', 0)) and \
                (chips.get('CO', 0) < chips.get('SB', 0)) and \
                (chips.get('CO', 0) < chips.get('BB', 0)):
            return True
        else:
            return False


class COCoversSB:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('CO', 0) < chips.get('BU', 0)) and \
                (chips.get('CO', 0) >= chips.get('SB', 0)) and \
                (chips.get('CO', 0) < chips.get('BB', 0)):
            return True
        else:
            return False


class COCoversBB:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('CO', 0) < chips.get('BU', 0)) and \
                (chips.get('CO', 0) < chips.get('SB', 0)) and \
                (chips.get('CO', 0) >= chips.get('BB', 0)):
            return True
        else:
            return False


class COCoversBUSB:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('CO', 0) >= chips.get('BU', 0)) and \
                (chips.get('CO', 0) >= chips.get('SB', 0)) and \
                (chips.get('CO', 0) < chips.get('BB', 0)):
            return True
        else:
            return False


class COCoversSBBB:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('CO', 0) < chips.get('BU', 0)) and \
                (chips.get('CO', 0) >= chips.get('SB', 0)) and \
                (chips.get('CO', 0) >= chips.get('BB', 0)):
            return True
        else:
            return False


class COCoversBUBB:
    def __call__(self, hh, **kwargs):

        try:
            chips = hh.position_chips
        except Exception as e:
            logger.exception(e)
            logger.exception(hh.hid)
            return False
        if (chips.get('CO', 0) >= chips.get('BU', 0)) and \
                (chips.get('CO', 0) < chips.get('SB', 0)) and \
                (chips.get('CO', 0) >= chips.get('BB', 0)):
            return True
        else:
            return False

