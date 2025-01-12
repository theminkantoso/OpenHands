from typing import TypedDict

from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config import AgentConfig
from openhands.core.schema import AgentState
from openhands.events.action import (
    Action,
    AgentFinishAction,
    AgentRejectAction,
    BrowseInteractiveAction,
    BrowseURLAction,
    CmdRunAction,
    FileReadAction,
    FileWriteAction,
    MessageAction, AgentDelegateAction,
)
from openhands.events.observation import (
    AgentStateChangedObservation,
    BrowserOutputObservation,
    CmdOutputMetadata,
    CmdOutputObservation,
    FileReadObservation,
    FileWriteObservation,
    NullObservation,
    Observation,
)
from openhands.events.serialization.event import event_to_dict
from openhands.llm.llm import LLM

ActionObs = TypedDict(
    'ActionObs', {'action': Action, 'observations': list[Observation]}
)


class MasterAgent(Agent):
    VERSION = '1.0'
    """
    Master Agent communicate with the user input and select planner or interaction agent
    """

    def __init__(self, llm: LLM, config: AgentConfig):
        super().__init__(llm, config)
        self.steps: list[ActionObs] = [
            {
                'action': MessageAction('Time to get started!'),
                'observations': [],
            },
            {
                'action': CmdRunAction(command='echo "foo"'),
                'observations': [CmdOutputObservation('foo', command='echo "foo"')],
            },
            {
                'action': FileWriteAction(
                    content='echo "Hello, World!"', path='hello.sh'
                ),
                'observations': [
                    FileWriteObservation(
                        content='echo "Hello, World!"', path='hello.sh'
                    )
                ],
            },
            {
                'action': FileReadAction(path='hello.sh'),
                'observations': [
                    FileReadObservation('echo "Hello, World!"\n', path='hello.sh')
                ],
            },
            {
                'action': CmdRunAction(command='bash hello.sh'),
                'observations': [
                    CmdOutputObservation(
                        'bash: hello.sh: No such file or directory',
                        command='bash workspace/hello.sh',
                        metadata=CmdOutputMetadata(exit_code=127),
                    )
                ],
            },
            {
                'action': BrowseURLAction(url='https://google.com'),
                'observations': [
                    BrowserOutputObservation(
                        '<html><body>Simulated Google page</body></html>',
                        url='https://google.com',
                        screenshot='',
                        trigger_by_action='',
                    ),
                ],
            },
            {
                'action': BrowseInteractiveAction(
                    browser_actions='goto("https://google.com")'
                ),
                'observations': [
                    BrowserOutputObservation(
                        '<html><body>Simulated Google page after interaction</body></html>',
                        url='https://google.com',
                        screenshot='',
                        trigger_by_action='',
                    ),
                ],
            },
            {
                'action': AgentRejectAction(),
                'observations': [NullObservation('')],
            },
            {
                'action': AgentFinishAction(
                    outputs={}, thought='Task completed', action='finish'
                ),
                'observations': [AgentStateChangedObservation('', AgentState.FINISHED)],
            },
        ]

    def step(self, state: State) -> Action:
        # if we're done, go back
        latest_user_message = state.get_last_user_message()
        if latest_user_message and latest_user_message.content.strip() == '/exit':
            return AgentFinishAction()

        if state.iteration >= len(self.steps):
            return AgentFinishAction()

        if state.iteration == 1:
            # Conversation init
            # TODO: Delegate to Planner Agent
            return AgentDelegateAction(agent='PlannerAgent', inputs={})
        else:
            # Interaction mode
            # TODO: Delegate to Interaction Agent
            return AgentDelegateAction(agent='InteractionAgent', inputs={})

        return MessageAction('Hello, World!')




