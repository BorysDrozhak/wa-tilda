from statemachine import StateMachine, State

class States(StateMachine):
    generate_poll = State('Generate')
    initial = State('Initial', initial=True)

    generate = initial.to(generate_poll)
    reset = generate_poll.to(initial)

state_obj = States()
