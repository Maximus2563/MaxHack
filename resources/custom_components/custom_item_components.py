from __future__ import annotations

from app.data.components import Type
from app.data.database import DB
from app.data.item_components import ItemComponent, ItemTags
from app.engine import (action, banner, combat_calcs, engine, equations,
                        image_mods, item_funcs, item_system, skill_system,
                        static_random, target_system)
from app.engine.game_state import game
from app.engine.objects.unit import UnitObject
from app.utilities import utils


class DoNothing(ItemComponent):
    nid = 'do_nothing'
    desc = 'does nothing'
    tag = ItemTags.CUSTOM

    expose = Type.Int
    value = 1
    
    class BlastAOE(ItemComponent):
    nid = 'blast_aoe'
    desc = "Blast extends outwards the specified number of tiles."
    tag = ItemTags.CUSTOM

    expose = Type.Int  # Radius
    value = 1

    def _get_power(self, unit) -> int:
        empowered_splash = skill_system.empower_splash(unit)
        return self.value + 1 + empowered_splash

    def splash(self, unit, item, position) -> tuple:
        ranges = set(range(self._get_power(unit)))
        splash = target_system.find_manhattan_spheres(ranges, position[0], position[1])
        splash = {pos for pos in splash if game.tilemap.check_bounds(pos)}
        from app.engine import item_system
        if item_system.is_spell(unit, item):
            # spell blast
            splash = [game.board.get_unit(s) for s in splash]
            splash = [s.position for s in splash if s]
            return None, splash
        else:
            # regular blast
            splash = [game.board.get_unit(s) for s in splash if s != position]
            splash = [s.position for s in splash if s]
            return position if game.board.get_unit(position) else None, splash

    def splash_positions(self, unit, item, position) -> set:
        ranges = set(range(self._get_power(unit)))
        splash = target_system.find_manhattan_spheres(ranges, position[0], position[1])
        splash = {pos for pos in splash if game.tilemap.check_bounds(pos)}
        return splash

class RallyBlastAOE(BlastAOE, ItemComponent):
    nid = 'rally_aoe'
    desc = "Gives Blast AOE that only hits non-user allies"
    tag = ItemTags.AOE

    def splash(self, unit, item, position) -> tuple:
        ranges = set(range(self._get_power(unit)))
        splash = target_system.find_manhattan_spheres(ranges, position[0], position[1])
        splash = {pos for pos in splash if game.tilemap.check_bounds(pos)}
        from app.engine import skill_system
        splash = [game.board.get_unit(s) for s in splash]
        splash = [s.position for s in splash if s and skill_system.check_ally(unit, s) and s is not unit]
        return None, splash
