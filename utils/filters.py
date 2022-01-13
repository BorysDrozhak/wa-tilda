from telegram.ext import MessageFilter

from utils.states import state_obj

class FilterTitle(MessageFilter):
    state = state_obj

    def filter(self, message):
        if 'Title' == self.state.current_state.name:
            return True

filter_initial = FilterTitle()


class AdditionalQuestions(MessageFilter):
    state = state_obj

    def filter(self, message):
        if 'Так' in message.text:
            return True

filter_additional = AdditionalQuestions()


class EndQuestions(MessageFilter):
    state = state_obj

    def filter(self, message):
        if 'Ні' in message.text:
            return True

filter_end_questions = EndQuestions()


class Questions(MessageFilter):
    state = state_obj

    def filter(self, message):
        if 'Questions' == self.state.current_state.name and message.text not in ['Так', 'Ні']:
            return True


filter_questions = Questions()