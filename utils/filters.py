from telegram.ext import MessageFilter

from utils.states import state_obj


class FilterGeneratePoll(MessageFilter):
    state = state_obj

    def filter(self, message):
        if 'Generate' == self.state.current_state.name and message.text == 'Так, звісно':
            return True


filter_generate = FilterGeneratePoll()


class FilterCancelPoll(MessageFilter):
    def filter(self, message):
        return 'Пропустити' in message.text


filter_cancel = FilterCancelPoll()