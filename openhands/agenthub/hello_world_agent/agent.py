from typing import TypedDict

from openhands.controller.agent import Agent
from openhands.controller.state.state import State
from openhands.core.config import AgentConfig
from openhands.core.schema import AgentState
from openhands.events.action import (
    Action,
    AddTaskAction,
    AgentFinishAction,
    AgentRejectAction,
    BrowseInteractiveAction,
    BrowseURLAction,
    CmdRunAction,
    FileReadAction,
    FileWriteAction,
    MessageAction,
    ModifyTaskAction,
)
from openhands.events.observation import (
    AgentStateChangedObservation,
    CmdOutputObservation,
    FileReadObservation,
    FileWriteObservation,
    NullObservation,
    Observation,
)
from openhands.llm.llm import LLM

"""
FIXME: There are a few problems this surfaced
* FileWrites seem to add an unintended newline at the end of the file
* Browser not working
"""

ActionObs = TypedDict(
    'ActionObs', {'action': Action, 'observations': list[Observation]}
)


class HelloWorldAgent(Agent):
    VERSION = '1.0'

    def __init__(self, llm: LLM, config: AgentConfig):
        super().__init__(llm, config)
        self.steps: list[ActionObs] = [
            {
                'action': AddTaskAction(
                    parent='None', goal='check the current directory'
                ),
                'observations': [],
            },
            {
                'action': AddTaskAction(parent='0', goal='run ls'),
                'observations': [],
            },
            {
                'action': ModifyTaskAction(task_id='0', state='in_progress'),
                'observations': [],
            },
            {
                'action': MessageAction('Time to get started!'),
                'observations': [],
            },
            {
                'action': CmdRunAction(command='echo "foo"'),
                'observations': [
                    CmdOutputObservation(
                        'foo', command_id=-1, command='echo "foo"', exit_code=0
                    )
                ],
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
                        command_id=-1,
                        command='bash workspace/hello.sh',
                        exit_code=127,
                    )
                ],
            },
            {
                'action': BrowseURLAction(url='https://google.com'),
                'observations': [
                    # BrowserOutputObservation('<html><body>Simulated Google page</body></html>',url='https://google.com',screenshot=''),
                ],
            },
            {
                'action': BrowseInteractiveAction(
                    browser_actions='goto("https://google.com")'
                ),
                'observations': [
                    # BrowserOutputObservation('<html><body>Simulated Google page after interaction</body></html>',url='https://google.com',screenshot=''),
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

    def reset(self) -> None:
        self.system_message = 'Hello, World!'

    def step(self, state: State) -> Action:
        return CmdRunAction(command='echo "Hello, World!"')
