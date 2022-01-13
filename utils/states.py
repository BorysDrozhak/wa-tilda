from statemachine import StateMachine, State

class States(StateMachine):
    title = State('Title')
    questions = State('Questions')
    initial = State('Initial', initial=True)

    slowdown = initial.to(title)
    question = title.to(questions)
    reverse = questions.to(initial)

state_obj = States()


class UserData:
    USER_DATA = {
        'title': None,
        'questions': []
    }

user_data = UserData()
