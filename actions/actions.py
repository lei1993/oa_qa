from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet

support_search = ["预订"]


def extract_item(item):
    if item is None:
        return None
    for name in support_search:
        if name in item:
            return name
    return None


class ActionSearchConsume(Action):
    def name(self):
        return 'action_search_consume'

    def run(self, dispatcher, tracker, domain):
        item = tracker.get_slot("item")
        item = extract_item(item)
        if item is None:
            dispatcher.utter_message("您好，我现在只会预订会议室")
            dispatcher.utter_message("你可以这样问我：“帮我预订今天下午三点到四点的会议室”")
            return []

        user_time_or_period = tracker.get_slot("user_time_or_period")
        if user_time_or_period is None:
            dispatcher.utter_message("请输入会议的日期和开始时间或时间段")
            return []
        user_loc = tracker.get_slot("user_loc")
        if user_loc is None:
            dispatcher.utter_message("请输入会议的地点")
            return []
        # query database here using item and time as key. but you may normalize time format first.
        dispatcher.utter_message("好，请稍等")

        if item == "预订":
            #dispatcher.utter_message(
            #    "您好，您{}共使用{}二百八十兆，剩余三十兆。".format(time, item))
            dispatcher.utter_message("您好，正在帮您预订！")
        else:
            dispatcher.utter_message("听不懂您在说什么")
        return []

