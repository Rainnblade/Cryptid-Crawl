import unittest
import copy
from unittest.mock import patch
import combat_state
import characters as chars_module


def _save_state():
    return (
        copy.deepcopy(chars_module.characters),
        copy.deepcopy(chars_module.enemies),
    )


def _restore_state(chars_backup, enemies_backup):
    chars_module.characters.clear()
    chars_module.characters.update(chars_backup)
    chars_module.enemies.clear()
    chars_module.enemies.update(enemies_backup)


# Requirement 7 Test - Turn Order
class TestTurnOrder(unittest.TestCase):

    def test_faster_combatant_goes_first(self):
        # Bear speed=30, Bigfoot speed=22 so Bear should go first
        result = combat_state.turn_order(['Bigfoot', 'Bear'])
        self.assertEqual(result[0], 'Bear')

    def test_all_combatants_returned(self): # Checks to make sure all party members are in the roster
        roster = ['Bigfoot', 'Bear', 'Mothman']
        result = combat_state.turn_order(roster)
        self.assertEqual(len(result), 3)


# Requirement 8 Test - Damage Calculations
class TestDamageCalc(unittest.TestCase):

    def setUp(self):
        self._chars_backup, self._enemies_backup = _save_state()

    def tearDown(self):
        _restore_state(self._chars_backup, self._enemies_backup)

    @patch('combat_state.random.randrange')
    def test_player_hit_returns_integer(self, mock_rand): # Forces a hit, expecting integer back
        mock_rand.side_effect = [1, 1]
        result = combat_state.damage_calc_player('Bigfoot', 'Bear', 'axe swing')
        self.assertIsInstance(result, int)

    @patch('combat_state.random.randrange')
    def test_player_miss_returns_missed(self, mock_rand): # Forces miss, expects 'missed' string to be returned
        # axe swing accuracy=80, roll 99 > 80 → miss
        mock_rand.side_effect = [1, 99]
        result = combat_state.damage_calc_player('Bigfoot', 'Bear', 'axe swing')
        self.assertEqual(result, 'missed')


# Requirement 9 Test - Update Stats
class TestUpdateStat(unittest.TestCase):

    def setUp(self):
        self._chars_backup, self._enemies_backup = _save_state()

    def tearDown(self):
        _restore_state(self._chars_backup, self._enemies_backup)

    def test_damage_reduces_character_hp(self): # Deals 5 damage, making sure health matches
        original = chars_module.characters['Bigfoot']['temp_health']
        combat_state.update_stat('Bigfoot', 5, 'temp_health', False)
        self.assertEqual(chars_module.characters['Bigfoot']['temp_health'], original - 5)

    def test_invalid_input_returns_false(self): # Passes a string instead of int, expects to return False
        result = combat_state.update_stat('Bear', 'abc', 'health', False)
        self.assertFalse(result)


# Requirement 10 Test - Apply Modifiers
class TestModifiers(unittest.TestCase):

    def setUp(self):
        self._chars_backup, self._enemies_backup = _save_state()

    def tearDown(self):
        _restore_state(self._chars_backup, self._enemies_backup)

    @patch('combat_state.random.randrange')
    def test_elemental_damage_higher_than_physical(self, mock_rand): # Testing multipliers
        # fire bolt (fire type, x1.5) vs axe swing (physical, no multiplier)
        # force hit, no crit for both
        mock_rand.side_effect = [1, 1]
        fire_result = combat_state.damage_calc_player('Mothman', 'Bear', 'fire bolt')

        mock_rand.side_effect = [1, 1]
        physical_result = combat_state.damage_calc_player('Bigfoot', 'Bear', 'axe swing')

        self.assertGreater(fire_result, physical_result)

    @patch('combat_state.random.randrange')
    def test_entangle_sets_enemy_effect(self, mock_rand): # Testing to see if enemy gains the 'entangle' status
        mock_rand.side_effect = [1, 1]
        combat_state.damage_calc_player('Selkie', 'Bear', 'entangle')
        self.assertEqual(chars_module.enemies['Bear']['effect'], 'entangled')


if __name__ == '__main__':
    unittest.main()
