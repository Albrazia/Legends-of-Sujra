from __future__ import annotations

from app.data.database.components import ComponentType
from app.data.database.database import DB
from app.data.database.skill_components import SkillComponent, SkillTags
from app.engine import (action, banner, combat_calcs, engine, equations,
                        image_mods, item_funcs, item_system, skill_system,
                        target_system)
from app.engine.game_state import game
from app.engine.objects.unit import UnitObject
from app.utilities import utils
from app.utilities import static_random
from app.engine.combat import playback as pb

class BackStep(SkillComponent):
    nid = 'backstep'
    desc = "Unit falls back after combat"
    tag = SkillTags.CUSTOM

    expose = ComponentType.Int
    value = 1

    def _check_backstep(self, unit_to_move, anchor, magnitude):
        offset_x = utils.clamp(unit_to_move.position[0] - anchor.position[0], -1, 1)
        offset_y = utils.clamp(unit_to_move.position[1] - anchor.position[1], -1, 1)
        new_position = (unit_to_move.position[0] + offset_x * self.value,
                        unit_to_move.position[1] + offset_y * self.value)
        if offset_x==0 ^ offset_y==0 :
            return False
        if game.board.check_bounds(new_position) and \
                not game.board.get_unit(new_position):
            return new_position
        return False

    def end_combat(self, playback, unit, item, target, mode):
        if not skill_system.ignore_forced_movement(target) and mode:
            new_position = self._check_backstep(unit, target, self.value)
            if new_position:
                print(unit.name)
                print(unit.position)
                print(new_position)
                action.do(action.ForcedMovement(unit, new_position))

class GoThrough(SkillComponent):
    nid = 'GoThrough'
    desc = "Unit goes through target after combat"
    tag = SkillTags.CUSTOM

    def _check_GoThrough(self, unit_to_move, anchor):
        offset_x = utils.clamp(anchor.position[0] - unit_to_move.position[0], -1, 1)
        offset_y = utils.clamp(anchor.position[1] - unit_to_move.position[1], -1, 1)
        new_position = (anchor.position[0] + offset_x,
                        anchor.position[1] + offset_y)

        if game.board.check_bounds(new_position) and \
                not game.board.get_unit(new_position):
            return new_position
        return False

    def end_combat(self, playback, unit, item, target, mode):
        if not skill_system.ignore_forced_movement(target) and mode:
            new_position = self._check_GoThrough(unit, target)
            if new_position:
                print(unit.name)
                print(unit.position)
                print(new_position)
                action.do(action.ForcedMovement(unit, new_position))

class Swap(SkillComponent):
    nid = 'battleswap'
    desc = "Unit swaps position with target"
    tag = SkillTags.CUSTOM

    def end_combat(self, playback, unit, item, target, mode):
        if not skill_system.ignore_forced_movement(target) and not skill_system.ignore_forced_movement(unit) and mode:
            action.do(action.Swap(unit, target))

class ComeOverHere(SkillComponent):
    nid = 'Come Over Here'
    desc= "Unit pulls a unit in front of him"
    tag = SkillTags.CUSTOM

    def _check_come(self, unit_to_move, anchor):
        offset_x = utils.clamp(unit_to_move.position[0] - anchor.position[0],-1,1)
        offset_y = utils.clamp(unit_to_move.position[1] - anchor.position[1],-1,1)
        new_position = (anchor.position[0] + offset_x, anchor.position[1] + offset_y)

        if not game.board.get_unit(new_position):
            return new_position
        return False

    def end_combat(self, playback, unit, item, target, mode):
        if not skill_system.ignore_forced_movement(target) and mode:
            new_position = self._check_come(target, unit)
            if new_position:
                action.do(action.ForcedMovement(target, new_position))

class WarpHpTreshhold(SkillComponent):
    nid = 'witch_hp'
    desc = 'Unit can warp to any ally who\'s hp is <=Value%'
    tag = SkillTags.CUSTOM

    expose = ComponentType.Int
    value = 50

    def witch_warp(self, unit: UnitObject)->Set[Tuple[int,int]]:
        warp_spots = set()
        for ally in game.get_all_units():
            if ally.team==unit.team and ally.position and game.board.check_bounds(ally.position):
                aHp=ally.get_hp()
                mHp=ally.get_max_hp()
                if(aHp<=(mHp*self.value/100)):
                    pos = ally.position
                    up = (pos[0], pos[1] - 1)
                    down = (pos[0], pos[1] + 1)
                    left = (pos[0] - 1, pos[1])
                    right = (pos[0] + 1, pos[1])
                    for point in [up, down, left, right]:
                        if game.board.check_bounds(point):
                            warp_spots.add(point)
        return warp_spots

class GetStatusAfterCombat(SkillComponent):
    nid = 'Get_status_after_combat'
    desc = "Gets a status to target after combat"
    tag = SkillTags.CUSTOM

    expose = ComponentType.Skill

    def end_combat(self, playback, unit, item, target, mode):
        from app.engine import skill_system
        if unit and skill_system.check_enemy(unit, target):
            action.do(action.AddSkill(unit, self.value, unit))
            action.do(action.TriggerCharge(unit, self.skill))

class CantoStatic(SkillComponent):
    nid = 'canto_Static'
    desc = "Unit can move X tiles after attacking"
    tag = SkillTags.MOVEMENT

    expose = ComponentType.Int
    value = 0

    def has_canto(self, unit, unit2) -> bool:
        unit.movement_left = self.value
        return True

class Specific2TileWitchWarp(SkillComponent):
    nid = 'specific_witch_warp_2_tiles'
    desc = "Allows unit to witch warp to the given unit 2 tiles around"
    tag = SkillTags.CUSTOM

    expose = (ComponentType.List, ComponentType.Unit)

    def witch_warp(self, unit) -> list:
        positions = set()
        for val in self.value:
            u = game.get_unit(val)
            if u and u.position:
                partner_pos = u.position
            else:
                continue
            if partner_pos:
                if game.board.check_bounds((partner_pos[0], partner_pos[1]-2)):
                    positions.add((partner_pos[0], partner_pos[1] - 2))
                if game.board.check_bounds((partner_pos[0]-1, partner_pos[1]-1)):
                    positions.add((partner_pos[0]-1, partner_pos[1]-1))
                if game.board.check_bounds((partner_pos[0], partner_pos[1]-1)):
                    positions.add((partner_pos[0], partner_pos[1]-1))
                if game.board.check_bounds((partner_pos[0]+1, partner_pos[1]-1)):
                    positions.add((partner_pos[0]+1, partner_pos[1]-1))
                if game.board.check_bounds((partner_pos[0]-2, partner_pos[1])):
                    positions.add((partner_pos[0]-2, partner_pos[1]))
                if game.board.check_bounds((partner_pos[0]-1, partner_pos[1])):
                    positions.add((partner_pos[0]-1, partner_pos[1]))
                if game.board.check_bounds((partner_pos[0]+1, partner_pos[1])):
                    positions.add((partner_pos[0]+1, partner_pos[1]))
                if game.board.check_bounds((partner_pos[0]+2, partner_pos[1])):
                    positions.add((partner_pos[0]+2, partner_pos[1]))
                if game.board.check_bounds((partner_pos[0]-1, partner_pos[1]+1)):
                    positions.add((partner_pos[0]-1, partner_pos[1]+1))
                if game.board.check_bounds((partner_pos[0], partner_pos[1]+1)):
                    positions.add((partner_pos[0], partner_pos[1]+1))
                if game.board.check_bounds((partner_pos[0]+1, partner_pos[1]+1)):
                    positions.add((partner_pos[0]+1, partner_pos[1]+1))
                if game.board.check_bounds((partner_pos[0], partner_pos[1]+2)):
                    positions.add((partner_pos[0], partner_pos[1]+2))  
        return positions

class HealOnHit(SkillComponent):
    nid = 'healonhit'
    desc = "Heals user the specified amount on hit"
    tag = SkillTags.COMBAT2

    expose = ComponentType.String
    value = 1

    def after_hit(self, actions, playback, unit, item, target, mode, attack_info):
        from app.engine import evaluate
        try:
            heal = int(evaluate.evaluate(self.value, unit, local_args={'item': item}))
        except:
            logging.error("Couldn't evaluate %s conditional" % self.value)

        actions.append(action.ChangeHP(unit, heal))

        playback.append(pb.HealHit(unit, item, unit, heal, heal))

        actions.append(action.TriggerCharge(unit, self.skill))

class Pivot(SkillComponent):
    nid = 'CombatPivot'
    desc= "Unit moves target behing it"
    tag = SkillTags.CUSTOM

    def _check_pivot(self, unit_to_move, anchor):
        offset_x = unit_to_move.position[0] - anchor.position[0]
        offset_y = unit_to_move.position[1] - anchor.position[1]
        new_position = (anchor.position[0] - offset_x, anchor.position[1] - offset_y)

        if not game.board.get_unit(new_position):
            return new_position
        return False

    def end_combat(self, playback, unit, item, target, mode):
        if not skill_system.ignore_forced_movement(target) and mode:
            new_position = self._check_pivot(target, unit)
            if new_position:
                action.do(action.ForcedMovement(target, new_position))