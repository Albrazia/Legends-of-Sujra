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

class CardinalRangeAOE(ItemComponent):
    nid = 'Cardinal_aoe'
    desc = "A line is drawn in every cardinal direction around the unit"
    tag = ItemTags.AOE

    expose = Type.Int
    value = 1

    def splash(self, unit, item, position) -> tuple:
        from app.engine import skill_system
        pos = unit.position
        all_positions=set()
        if pos[0]-position[0]>=1 :
            for x in range(self.value+1):
                all_positions.add((pos[0]-x,pos[1]))
        elif pos[0]-position[0]<=-1 :
            for x in range(self.value+1):
                all_positions.add((pos[0]+x,pos[1]))
        elif pos[1]-position[1]>=1 :
            for x in range(self.value+1):
                all_positions.add((pos[0],pos[1]-x))
        elif pos[1]-position[1]<=-1 :
            for x in range(self.value+1):
                all_positions.add((pos[0],pos[1]+x))
        else: 
            for x in range(self.value+1):
                all_positions.add((pos[0]-x,pos[1]))
                all_positions.add((pos[0]+x,pos[1]))
                all_positions.add((pos[0],pos[1]-x))
                all_positions.add((pos[0],pos[1]+x))
        all_positions = {pos for pos in all_positions if game.tilemap.check_bounds(pos)}
        all_positions.discard(position)
        splash = all_positions
        splash = [game.board.get_unit(pos) for pos in splash]
        splash = [s.position for s in splash if s and skill_system.check_enemy(unit, s)]
        return None, splash

    def splash_positions(self, unit, item, position) -> set:
        from app.engine import skill_system
        pos = unit.position
        all_positions=set()
        if pos[0]-position[0]>=1 :
            for x in range(self.value+1):
                all_positions.add((pos[0]-x,pos[1]))
        elif pos[0]-position[0]<=-1 :
            for x in range(self.value+1):
                all_positions.add((pos[0]+x,pos[1]))
        elif pos[1]-position[1]>=1 :
            for x in range(self.value+1):
                all_positions.add((pos[0],pos[1]-x))
        elif pos[1]-position[1]<=-1 :
            for x in range(self.value+1):
                all_positions.add((pos[0],pos[1]+x))
        else: 
            for x in range(self.value+1):
                all_positions.add((pos[0]-x,pos[1]))
                all_positions.add((pos[0]+x,pos[1]))
                all_positions.add((pos[0],pos[1]-x))
                all_positions.add((pos[0],pos[1]+x))
        all_positions = {pos for pos in all_positions if game.tilemap.check_bounds(pos)}
        all_positions.discard(position)
        splash = all_positions
        # Doesn't highlight allies positions
        splash = {pos for pos in splash if not game.board.get_unit(pos) or skill_system.check_enemy(unit, game.board.get_unit(pos))}
        return splash

class Conic3AOE(ItemComponent):
    nid = 'Conic_3_aoe'
    desc = "A coned range AOE"
    tag = ItemTags.AOE

    def splash(self, unit, item, position) -> tuple:
        from app.engine import skill_system
        pos = unit.position
        all_positions=set()
        if pos[0]-position[0]>=1 :
            #West
            all_positions.add((pos[0]-1,pos[1]))

            all_positions.add((pos[0]-2,pos[1]-1))
            all_positions.add((pos[0]-2,pos[1]))
            all_positions.add((pos[0]-2,pos[1]+1))

            all_positions.add((pos[0]-3,pos[1]-2))
            all_positions.add((pos[0]-3,pos[1]-1))
            all_positions.add((pos[0]-3,pos[1]))
            all_positions.add((pos[0]-3,pos[1]+1))
            all_positions.add((pos[0]-3,pos[1]+2))
        elif pos[0]-position[0]<=-1 :
            #East
            all_positions.add((pos[0]+1,pos[1]))

            all_positions.add((pos[0]+2,pos[1]-1))
            all_positions.add((pos[0]+2,pos[1]))
            all_positions.add((pos[0]+2,pos[1]+1))

            all_positions.add((pos[0]+3,pos[1]-2))
            all_positions.add((pos[0]+3,pos[1]-1))
            all_positions.add((pos[0]+3,pos[1]))
            all_positions.add((pos[0]+3,pos[1]+1))
            all_positions.add((pos[0]+3,pos[1]+2))
        elif pos[1]-position[1]>=1 :
            #North
            all_positions.add((pos[0],pos[1]-1))

            all_positions.add((pos[0]-1,pos[1]-2))
            all_positions.add((pos[0],pos[1]-2))
            all_positions.add((pos[0]+1,pos[1]-2))

            all_positions.add((pos[0]-2,pos[1]-3))
            all_positions.add((pos[0]-1,pos[1]-3))
            all_positions.add((pos[0],pos[1]-3))
            all_positions.add((pos[0]+1,pos[1]-3))
            all_positions.add((pos[0]+2,pos[1]-3))
        elif pos[1]-position[1]<=-1 :
            #South
            all_positions.add((pos[0],pos[1]+1))

            all_positions.add((pos[0]-1,pos[1]+2))
            all_positions.add((pos[0],pos[1]+2))
            all_positions.add((pos[0]+1,pos[1]+2))

            all_positions.add((pos[0]-2,pos[1]+3))
            all_positions.add((pos[0]-1,pos[1]+3))
            all_positions.add((pos[0],pos[1]+3))
            all_positions.add((pos[0]+1,pos[1]+3))
            all_positions.add((pos[0]+2,pos[1]+3))
        else: 
            all_positions.add(pos)
        all_positions = {pos for pos in all_positions if game.tilemap.check_bounds(pos)}
        all_positions.discard(position)
        splash = all_positions
        splash = [game.board.get_unit(pos) for pos in splash]
        splash = [s.position for s in splash if s and skill_system.check_enemy(unit, s)]
        return None, splash

    def splash_positions(self, unit, item, position) -> set:
        from app.engine import skill_system
        pos = unit.position
        all_positions=set()
        if pos[0]-position[0]>=1 :
            #West
            all_positions.add((pos[0]-1,pos[1]))

            all_positions.add((pos[0]-2,pos[1]-1))
            all_positions.add((pos[0]-2,pos[1]))
            all_positions.add((pos[0]-2,pos[1]+1))

            all_positions.add((pos[0]-3,pos[1]-2))
            all_positions.add((pos[0]-3,pos[1]-1))
            all_positions.add((pos[0]-3,pos[1]))
            all_positions.add((pos[0]-3,pos[1]+1))
            all_positions.add((pos[0]-3,pos[1]+2))
        elif pos[0]-position[0]<=-1 :
            #East
            all_positions.add((pos[0]+1,pos[1]))

            all_positions.add((pos[0]+2,pos[1]-1))
            all_positions.add((pos[0]+2,pos[1]))
            all_positions.add((pos[0]+2,pos[1]+1))

            all_positions.add((pos[0]+3,pos[1]-2))
            all_positions.add((pos[0]+3,pos[1]-1))
            all_positions.add((pos[0]+3,pos[1]))
            all_positions.add((pos[0]+3,pos[1]+1))
            all_positions.add((pos[0]+3,pos[1]+2))
        elif pos[1]-position[1]>=1 :
            #North
            all_positions.add((pos[0],pos[1]-1))

            all_positions.add((pos[0]-1,pos[1]-2))
            all_positions.add((pos[0],pos[1]-2))
            all_positions.add((pos[0]+1,pos[1]-2))

            all_positions.add((pos[0]-2,pos[1]-3))
            all_positions.add((pos[0]-1,pos[1]-3))
            all_positions.add((pos[0],pos[1]-3))
            all_positions.add((pos[0]+1,pos[1]-3))
            all_positions.add((pos[0]+2,pos[1]-3))
        elif pos[1]-position[1]<=-1 :
            #South
            all_positions.add((pos[0],pos[1]+1))

            all_positions.add((pos[0]-1,pos[1]+2))
            all_positions.add((pos[0],pos[1]+2))
            all_positions.add((pos[0]+1,pos[1]+2))

            all_positions.add((pos[0]-2,pos[1]+3))
            all_positions.add((pos[0]-1,pos[1]+3))
            all_positions.add((pos[0],pos[1]+3))
            all_positions.add((pos[0]+1,pos[1]+3))
            all_positions.add((pos[0]+2,pos[1]+3))
        else: 
            all_positions.add(pos)
        all_positions = {pos for pos in all_positions if game.tilemap.check_bounds(pos)}
        all_positions.discard(position)
        splash = all_positions
        # Doesn't highlight allies positions
        splash = {pos for pos in splash if not game.board.get_unit(pos) or skill_system.check_enemy(unit, game.board.get_unit(pos))}
        return splash
        
class ComeOverHere(ItemComponent):
    nid = 'Come Over Here'
    desc= "Unit pulls an ennemys in front of him"
    tag = ItemTags.CUSTOM

    def _check_come(self, unit_to_move, anchor):
        offset_x = utils.clamp(unit_to_move.position[0] - anchor.position[0],-1,1)
        offset_y = utils.clamp(unit_to_move.position[1] - anchor.position[1],-1,1)
        new_positionX = (anchor.position[0] + offset_x, anchor.position[1])
        new_positionY = (anchor.position[0], + anchor.position[1]+offset_y)
        if not game.board.get_unit(new_positionX) and offset_x:
            return new_positionX
        elif not game.board.get_unit(new_positionY) and offset_y:
            return new_positionY
        else:
            return False

    def on_hit(self, actions, playback, unit, item, target, target_pos, mode, attack_info):
        if not skill_system.ignore_forced_movement(target):
            new_position = self._check_come(target, unit)
            if new_position:
                actions.append(action.ForcedMovement(target, new_position))
                playback.append(('shove_hit', unit, item, target))

class CardinalTilesRange(ItemComponent):
    nid = 'Cardinal Range'
    desc = 'Item targets tile in the cardinal range exclusively'
    tag=ItemTags.CUSTOM

    expose = Type.Int
    value = 0
    def valid_target(self, unit, item) -> set:
        rng = item_funcs.get_range(unit, item)
        range_restrictions = set()
        for x in range(value+1):
            range_restrictions.add((unit.position[0]-x,unit.position[1]))
            range_restrictions.add((unit.position[0]+x,unit.position[1]))
            range_restrictions.add((unit.position[0],unit.position[1]-x))
            range_restrictions.add((unit.position[0],unit.position[1]+x))
        targetable_positions = self.resolve_targets()
        return {pos for pos in targetable_positions if pos in range_restrictions}

    def resolve_targets(self):
        from app.engine import evaluate
        value_list = evaluate.evaluate(self.value)
        return utils.flatten_list(value_list)

        
class TrueDamage(ItemComponent):
    nid = 'truedamage'
    desc = "Item does irreductible damage on hit (no hit restrict)"
    tag = ItemTags.CUSTOM

    expose = Type.Int
    value = 0

    def damage(self, unit, item):
        return self.value

    def on_hit(self, actions, playback, unit, item, target, target_pos, mode, attack_info):
        playback_nids = [_[0] for _ in playback]
        if 'attacker_partner_phase' in playback_nids or 'defender_partner_phase' in playback_nids:
            damage = self.value
        else:
            damage = self.value

        true_damage = min(damage, target.get_hp())
        actions.append(action.ChangeHP(target, -damage))

        # For animation
        playback.append(('damage_hit', unit, item, target, damage, true_damage))
        if damage == 0:
            playback.append(('hit_sound', 'No Damage'))
            playback.append(('hit_anim', 'MapNoDamage', target))

    def on_glancing_hit(self, actions, playback, unit, item, target, target_pos, mode, attack_info):
        playback_nids = [_[0] for _ in playback]
        if 'attacker_partner_phase' in playback_nids or 'defender_partner_phase' in playback_nids:
            damage = self.value
        else:
            damage = self.value
        damage //= 2  # Because glancing hit

        true_damage = min(damage, target.get_hp())
        actions.append(action.ChangeHP(target, -damage))

        # For animation
        playback.append(('damage_hit', unit, item, target, damage, true_damage))
        if damage == 0:
            playback.append(('hit_anim', 'MapNoDamage', target))

class StatusOnUse(ItemComponent):
    nid = 'status_on_use'
    desc = "User gains the specified status on use."
    tag = ItemTags.CUSTOM

    expose = Type.Skill  # Nid

    def on_hit(self, actions, playback, unit, item, target, target_pos, mode, attack_info):
        act = action.AddSkill(unit, self.value, unit)
        actions.append(act)

    def ai_priority(self, unit, item, target, move):
        # Do I add a new status to the target
        return ai_status_priority(unit, target, item, move, self.value)