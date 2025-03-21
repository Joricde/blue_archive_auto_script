import time

from core import image, picture
from module import hard_task, main_story, normal_task


def get_challenge_state(self, challenge_count=1) -> list[int]:
    """
        Returns:
            list[int] :
                - int = 0, challenge unfinished
                - int = 1, challenge finished
                - int = -1, challenge state unknown
    """

    # to challenge menu
    challenge_button_y = {
        'CN': 272,
        'Global': 302,
        'JP': 302
    }
    img_ends = 'normal_task_challenge-menu'
    img_possibles = {
        "normal_task_challenge-button": (536, challenge_button_y[self.server]),
        "activity_quest-challenge-button": (319, 270)
    }
    picture.co_detect(self, None, None, img_ends, img_possibles, True)

    result = []
    for i in range(1, challenge_count + 1):
        if image.compare_image(self, "normal_task_challenge" + str(i) + "-unfinished", 0.8, 10):
            result.append(0)
        elif image.compare_image(self, "normal_task_challenge" + str(i) + "-finished", 0.8, 10):
            result.append(1)
        else:
            result.append(-1)
    to_mission_info(self)
    return result


def to_region(self, region, isNormal: bool):
    square = {
        'CN': [122, 178, 163, 208],
        'Global': [122, 178, 163, 208],
        'JP': [122, 178, 163, 208]
    }
    curRegion = self.ocr.get_region_num(self.latest_img_array, square[self.server], int, self.ratio)
    self.logger.info("Current Region : " + str(curRegion))
    while curRegion != region and self.flag_run:
        if curRegion > region:
            self.click(40, 360, count=curRegion - region, rate=0.1, wait_over=True)
        else:
            self.click(1245, 360, count=region - curRegion, rate=0.1, wait_over=True)
        # TODO 检测是否是未解锁区域
        time.sleep(0.5)
        if isNormal:
            normal_task.to_normal_event(self)
        else:
            hard_task.to_hard_event(self)
        curRegion = self.ocr.get_region_num(self.latest_img_array, square[self.server], int, self.ratio)
        self.logger.info("Current Region : " + str(curRegion))


def retreat(self):
    rgb_possibles = {"fighting_feature": (1226, 51)}
    img_possible = {
        'normal_task_fight-pause': (908, 508),
        'normal_task_retreat-notice': (768, 507)
    }
    img_ends = 'normal_task_fail-confirm'
    picture.co_detect(self, None, rgb_possibles, img_ends, img_possible, True)


def formation_attr_to_cn(attr):
    if attr.startswith('pierce'):
        return '贯穿'
    elif attr.startswith('burst'):
        return '爆发'
    elif attr.startswith('mystic'):
        return '神秘'
    elif attr.startswith('shock'):
        return '振动'
    return None


def execute_grid_task(self, taskData):
    img_possibles = {
        'normal_task_help': (1017, 131),
        'normal_task_task-info': (946, 540),
        'activity_task-info': (946, 540),
        "plot_menu": (1205, 34),
        "plot_skip-plot-button": (1213, 116),
        "plot_skip-plot-notice": (766, 520),
    }
    img_ends = "normal_task_task-wait-to-begin-feature"
    picture.co_detect(self, None, None, img_ends, img_possibles, True)
    choose_team_according_to_stage_data_and_config(self, taskData)
    start_mission(self)
    set_skip_and_auto_over(self)
    start_action(self, taskData['action'])


def task_mission_operating(self, skip_first_screenshot=False):
    img_possibles = {
        "normal_task_mission-operating-task-info-notice": (995, 101),
        "normal_task_end-turn": (890, 162),
        "normal_task_teleport-notice": (886, 162),
        'normal_task_present': (640, 519),
        "normal_task_fight-confirm": (1171, 670),
        'normal_task_fail-confirm': (640, 670),
    }
    img_ends = "normal_task_task-operating-feature"
    img_pop_ups = {"activity_choose-buff": (644, 570)}
    picture.co_detect(self, None, None, img_ends, img_possibles, skip_first_screenshot, img_pop_ups=img_pop_ups)


def turn_off_skip_fight(self) -> None:
    while self.flag_run:
        task_mission_operating(self, False)
        if image.compare_image(self, 'normal_task_fight-skip'):
            self.click(1194, 547, wait_over=True, duration=0.5)
        else:
            return


def set_skip_and_auto_over(self) -> None:
    while self.flag_run:
        finish_adjustment = True
        if not image.compare_image(self, 'normal_task_fight-skip'):
            finish_adjustment = False
            self.click(1194, 547, wait_over=True, duration=0.5)
        if not image.compare_image(self, 'normal_task_auto-over'):
            finish_adjustment = False
            self.click(1194, 600, wait_over=True, duration=0.5)
        if finish_adjustment:
            return
        task_mission_operating(self, False)


def wait_formation_change(self, force_index):
    self.logger.info("Wait formation change")
    origin = force_index
    while force_index == origin and self.flag_run:
        force_index = get_force(self)
        time.sleep(self.screenshot_interval)
    return force_index


def start_mission(self):
    img_ends = "normal_task_task-operating-feature"
    img_possibles = {
        'normal_task_task-begin-without-further-editing-notice': (768, 498),
        'normal_task_task-operating-round-over-notice': (888, 163),
        'normal_task_task-wait-to-begin-feature': (1171, 670),
        'normal_task_end-turn': (888, 163),
    }
    picture.co_detect(self, None, None, img_ends, img_possibles, True)
    wait_over(self)
    task_mission_operating(self, True)


def start_action(self, actions):
    self.set_screenshot_interval(1)
    self.logger.info("Start Actions total : " + str(len(actions)))
    for i, act in enumerate(actions):
        desc = "start " + str(i + 1) + " operation : "
        if 'desc' in act:
            desc += act['desc']
        self.logger.info(desc)
        force_index = get_force(self)
        op = act['t']
        if 'pre-wait' in act:
            time.sleep(act['pre-wait'])
        if 'retreat' in act:
            turn_off_skip_fight(self)
        if type(op) is str:
            op = [op]
        if 'p' in act:
            if type(act['p']) is tuple or (len(act['p']) == 2 and type(act['p'][0]) is int):
                act['p'] = [act['p']]
        skip_first_screenshot = False
        for j in range(0, len(op)):
            time.sleep(1)
            if op[j] == 'click':
                pos = act['p'][0]
                self.click(pos[0], pos[1], wait_over=True)
            elif op[j] == 'teleport':
                confirm_teleport(self)
            elif op[j] == 'exchange':
                self.click(83, 557, wait_over=True)
                force_index = wait_formation_change(self, force_index)
            elif op[j] == 'exchange_twice':
                self.click(83, 557, wait_over=True)
                force_index = wait_formation_change(self, force_index)
                self.click(83, 557, wait_over=True)
                force_index = wait_formation_change(self, force_index)
            elif op[j] == 'end-turn':
                end_turn(self)
                if i != len(actions) - 1:
                    if 'end-turn-wait-over' in act and act[
                        'end-turn-wait-over'] is False:  # not every end turn need to wait
                        self.logger.info("End Turn without wait over")
                    else:
                        wait_over(self)
                        skip_first_screenshot = True
            elif op[j] == 'click_and_teleport':
                pos = act['p'][0]
                self.click(pos[0], pos[1], wait_over=True)
                confirm_teleport(self)
            elif op[j] == 'choose_and_change':
                pos = act['p'][0]
                self.click(pos[0], pos[1], wait_over=True, duration=0.3)
                self.click(pos[0] - 100, pos[1], wait_over=True, duration=1)
            elif op[j] == 'exchange_and_click':
                self.click(83, 557, wait_over=True)
                force_index = wait_formation_change(self, force_index)
                time.sleep(0.5)
                pos = act['p'][0]
                self.click(pos[0], pos[1], wait_over=True)
            elif op[j] == 'exchange_twice_and_click':
                self.click(83, 557, wait_over=True)
                force_index = wait_formation_change(self, force_index)
                self.click(83, 557, wait_over=True)
                force_index = wait_formation_change(self, force_index)
                time.sleep(0.5)
                pos = act['p'][0]
                self.click(pos[0], pos[1], wait_over=True)
        if 'retreat' in act:
            for fight in range(1, act['retreat'][0] + 1):
                main_story.auto_fight(self)
                for retreatNum in act['retreat'][1:]:
                    if retreatNum == fight:
                        self.logger.info("retreat at fight" + str(retreatNum))
                        retreat(self)
                        break
                task_mission_operating(self, False)
            set_skip_and_auto_over(self)
        if 'ec' in act:
            wait_formation_change(self, force_index)
        if 'wait-over' in act:
            wait_over(self)
            skip_first_screenshot = True
            time.sleep(2)
        if 'post-wait' in act:
            time.sleep(act['post-wait'])
        if i != len(actions) - 1:
            task_mission_operating(self, skip_first_screenshot=skip_first_screenshot)
    self.set_screenshot_interval(self.config.screenshot_interval)


def get_force(self):
    region = {
        'CN': (116, 542, 131, 570),
        'Global': (116, 542, 131, 570),
        'JP': (116, 542, 131, 570)
    }
    task_mission_operating(self)
    ocr_res = self.ocr.get_region_num(self.latest_img_array, region[self.server], int, self.ratio)
    if ocr_res == "UNKNOWN":
        return get_force(self)
    if ocr_res == 7:
        ocr_res = 1
    if ocr_res not in [1, 2, 3, 4]:
        return get_force(self)
    self.logger.info("Current force : " + str(ocr_res))
    return ocr_res


def end_turn(self):
    self.logger.info("--End Turn--")
    img_end = 'normal_task_end-turn'
    img_possibles = {
        'normal_task_task-operating-feature': (1170, 670),
        'normal_task_present': (640, 519),
    }
    picture.co_detect(self, None, None, img_end, img_possibles)
    self.logger.info("Confirm End Turn")
    img_end = 'normal_task_task-operating-feature'
    img_possibles = {'normal_task_end-turn': (767, 501)}
    rgb_end = "fighting_feature"
    picture.co_detect(self, rgb_end, None, img_end, img_possibles, True)


def wait_over(self):
    self.logger.info("Wait until move available")
    img_ends = "normal_task_mission-operating-task-info-notice"
    img_possibles = {
        'normal_task_task-operating-feature': (997, 670),
        'normal_task_teleport-notice': (885, 164),
        "normal_task_fight-confirm": (1171, 670),
        'normal_task_present': (640, 519),
    }
    picture.co_detect(self, None, None, img_ends, img_possibles, True, rgb_pop_ups={"fighting_feature": (-1, -1)},
                      img_pop_ups={"activity_choose-buff": (644, 570)})


def confirm_teleport(self):
    self.logger.info("Wait Teleport Notice")
    picture.co_detect(self, None, None, "normal_task_teleport-notice", None)
    self.logger.info("Confirm Teleport")
    img_end = 'normal_task_task-operating-feature'
    img_possibles = {'normal_task_teleport-notice': (767, 501), }
    picture.co_detect(self, None, None, img_end, img_possibles, True)


def choose_team_according_to_stage_data_and_config(self, taskData):
    res, los = calc_team_number(self, taskData)
    for j in range(0, len(res)):
        if res[j] == "swipe":
            time.sleep(1)
            self.swipe(los[j][0], los[j][1], los[j][2], los[j][3], duration=los[j][4])
            time.sleep(1)
        else:
            choose_team(self, res[j], los[j], True)


def to_mission_info(self, y=0):
    rgb_possibles = {"event_hard": (1114, y), "event_normal": (1114, y)}
    img_ends = [
        "normal_task_task-info",
        "activity_task-info",
        "normal_task_SUB"
    ]
    img_possibles = {
        'normal_task_select-area': (1114, y),
        'normal_task_challenge-menu': (640, 490)
    }
    picture.co_detect(self, None, rgb_possibles, img_ends, img_possibles, True)


def choose_team(self, number, position, skip_first_screenshot=False):
    self.logger.info("According to the config. Choose team " + str(number))
    to_formation_edit_i(self, number, position, skip_first_screenshot)
    to_normal_task_wait_to_begin_page(self, skip_first_screenshot)


def calc_team_number(self, taskData):
    pri = {
        'pierce1': ['pierce1', 'pierce2', 'burst1', 'burst2', 'mystic1', 'mystic2', 'shock1', 'shock2'],
        'pierce2': ['pierce2', 'burst1', 'burst2', 'mystic1', 'mystic2', 'shock1', 'shock2'],
        'burst1': ['burst1', 'burst2', 'mystic1', 'mystic2', 'shock1', 'shock2', 'pierce1', 'pierce2'],
        'burst2': ['burst2', 'mystic1', 'mystic2', 'shock1', 'shock2', 'pierce1', 'pierce2'],
        'mystic1': ['mystic1', 'mystic2', 'shock1', 'shock2', 'burst1', 'burst2', 'pierce1', 'pierce2'],
        'mystic2': ['mystic2', 'burst1', 'shock1', 'shock2', 'burst2', 'pierce1', 'pierce2'],
        'shock1': ['shock1', 'shock2', 'pierce1', 'pierce2', 'mystic1', 'mystic2', 'burst1', 'burst2'],
        'shock2': ['shock2', 'pierce1', 'pierce2', 'mystic1', 'mystic2', 'burst1', 'burst2']
    }
    used = {
        'pierce1': False,
        'pierce2': False,
        'burst1': False,
        'burst2': False,
        'mystic1': False,
        'mystic2': False,
        'shock1': False,
        'shock2': False,
    }
    keys = used.keys()
    total_teams = 0
    for i in range(0, len(taskData['start'])):
        if taskData['start'][i][0] in keys:
            total_teams += 1
    last_chosen = 0
    team_res = []
    team_attr = []
    los = []
    for i in range(0, len(taskData['start'])):
        attr, position = taskData['start'][i][0], taskData['start'][i][1]
        los.append(position)
        if attr not in keys:
            continue
        for j in range(0, len(pri[attr])):
            possible_attr = pri[attr][j]
            if (possible_attr == 'shock1' or possible_attr == 'shock2') and self.server == 'CN':
                continue
            possible_index = int(self.config_set.get(possible_attr))
            if not used[possible_attr] and 4 - possible_index >= total_teams - len(team_res) - 1 and last_chosen < possible_index:
                team_res.append(possible_index)
                team_attr.append(possible_attr)
                used[possible_attr] = True
                last_chosen = possible_index
                break
    if len(team_res) != total_teams:
        self.logger.warning("Insufficient forces are chosen")
        if total_teams - len(team_res) <= 4 - last_chosen:
            for i in range(0, total_teams - len(team_res)):
                team_res.append(last_chosen + i + 1)
                team_attr.append("auto-choose")
        else:
            self.logger.warning("USE formations as the number increase")
            team_res.clear()
            team_attr = ["auto-choose"]
            cnt = 1
            for i in range(0, len(taskData['start'])):
                if taskData['start'][i][0] in keys:
                    team_res.append(cnt)
                    los.append(taskData['start'][i][1])
                    cnt += 1
    self.logger.info("Choose formations : " + str(team_res))
    self.logger.info("attr : " + str(team_attr))
    action_res = []
    temp = 0
    for i in range(0, len(taskData['start'])):
        if taskData['start'][i][0] not in keys:
            action_res.append(taskData['start'][i][0])
        else:
            action_res.append(team_res[temp])
            temp += 1
    self.logger.info("actions : " + str(action_res))
    self.logger.info("position : " + str(los))
    return action_res, los


def to_normal_task_wait_to_begin_page(self, skip_first_screenshot=False):
    rgb_possibles = {
        "formation_edit1": (1154, 625),
        "formation_edit2": (1154, 625),
        "formation_edit3": (1154, 625),
        "formation_edit4": (1154, 625),
    }
    img_ends = [
        'normal_task_task-wait-to-begin-feature',
        'normal_task_task-operating-feature'
    ]
    img_possibles = {
        'task-begin-without-further-editing-notice': (888, 164)
    }
    picture.co_detect(self, None, rgb_possibles, img_ends, img_possibles, skip_first_screenshot)


def to_formation_edit_i(self, i, lo, skip_first_screenshot=False):
    loy = [195, 275, 354, 423]
    y = loy[i - 1]
    rgb_ends = "formation_edit" + str(i)
    rgb_possibles = {
        "formation_edit1": (74, y),
        "formation_edit2": (74, y),
        "formation_edit3": (74, y),
        "formation_edit4": (74, y),
    }
    rgb_possibles.pop("formation_edit" + str(i))
    img_possibles = {"normal_task_task-wait-to-begin-feature": lo}
    picture.co_detect(self, rgb_ends, rgb_possibles, None, img_possibles, skip_first_screenshot)
