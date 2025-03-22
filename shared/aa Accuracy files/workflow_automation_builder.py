import logging
from typing import List, Dict, Any, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("workflow_automation_builder.log"),
        logging.StreamHandler()
    ]
)

class WorkflowAutomationBuilder:
    """
    A builder class for creating and managing automated workflows across RLG Data and RLG Fans.
    Provides capabilities to automate tasks, trigger actions, and integrate with various social media platforms.
    """

    def __init__(self):
        self.workflows = []  # List to store workflows
        logging.info("WorkflowAutomationBuilder initialized.")

    def create_workflow(self, name: str, triggers: List[Dict[str, Any]], actions: List[Callable]) -> Dict[str, Any]:
        """
        Create a new workflow.

        Args:
            name (str): Name of the workflow.
            triggers (List[Dict[str, Any]]): List of triggers that initiate the workflow.
            actions (List[Callable]): List of actions to execute when the workflow is triggered.

        Returns:
            Dict[str, Any]: The created workflow.
        """
        workflow = {
            "name": name,
            "triggers": triggers,
            "actions": actions,
            "active": True
        }
        self.workflows.append(workflow)
        logging.info("Workflow '%s' created.", name)
        return workflow

    def trigger_workflow(self, name: str, trigger_data: Dict[str, Any]) -> None:
        """
        Trigger a workflow by its name.

        Args:
            name (str): Name of the workflow to trigger.
            trigger_data (Dict[str, Any]): Data to evaluate the triggers.
        """
        workflow = next((wf for wf in self.workflows if wf["name"] == name and wf["active"]), None)

        if not workflow:
            logging.error("Workflow '%s' not found or inactive.", name)
            return

        # Check triggers
        for trigger in workflow["triggers"]:
            if not self._evaluate_trigger(trigger, trigger_data):
                logging.info("Trigger condition not met for workflow '%s'.", name)
                return

        # Execute actions
        logging.info("Trigger conditions met. Executing actions for workflow '%s'.", name)
        for action in workflow["actions"]:
            try:
                action(trigger_data)
            except Exception as e:
                logging.error("Error executing action in workflow '%s': %s", name, e)

    def _evaluate_trigger(self, trigger: Dict[str, Any], trigger_data: Dict[str, Any]) -> bool:
        """
        Evaluate if a trigger condition is met.

        Args:
            trigger (Dict[str, Any]): Trigger definition.
            trigger_data (Dict[str, Any]): Data to evaluate the trigger against.

        Returns:
            bool: True if the trigger condition is met, False otherwise.
        """
        try:
            key = trigger["key"]
            value = trigger["value"]
            condition = trigger["condition"]

            if condition == "equals":
                return trigger_data.get(key) == value
            elif condition == "contains":
                return value in trigger_data.get(key, "")
            elif condition == "greater_than":
                return trigger_data.get(key, 0) > value
            elif condition == "less_than":
                return trigger_data.get(key, 0) < value
            else:
                logging.warning("Unknown trigger condition '%s'.", condition)
                return False
        except Exception as e:
            logging.error("Error evaluating trigger: %s", e)
            return False

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows.

        Returns:
            List[Dict[str, Any]]: List of workflows.
        """
        logging.info("Listing all workflows.")
        return self.workflows

    def deactivate_workflow(self, name: str) -> None:
        """
        Deactivate a workflow by its name.

        Args:
            name (str): Name of the workflow to deactivate.
        """
        for workflow in self.workflows:
            if workflow["name"] == name:
                workflow["active"] = False
                logging.info("Workflow '%s' deactivated.", name)
                return
        logging.error("Workflow '%s' not found.", name)

    def activate_workflow(self, name: str) -> None:
        """
        Activate a workflow by its name.

        Args:
            name (str): Name of the workflow to activate.
        """
        for workflow in self.workflows:
            if workflow["name"] == name:
                workflow["active"] = True
                logging.info("Workflow '%s' activated.", name)
                return
        logging.error("Workflow '%s' not found.", name)

# Example Usage
def sample_action(data):
    logging.info("Executing sample action with data: %s", data)

if __name__ == "__main__":
    builder = WorkflowAutomationBuilder()

    # Create a sample workflow
    builder.create_workflow(
        name="Sample Workflow",
        triggers=[
            {"key": "event_type", "value": "page_view", "condition": "equals"},
            {"key": "page", "value": "dashboard", "condition": "equals"}
        ],
        actions=[sample_action]
    )

    # Trigger the workflow
    builder.trigger_workflow(
        name="Sample Workflow",
        trigger_data={"event_type": "page_view", "page": "dashboard"}
    )

    # List workflows
    workflows = builder.list_workflows()
    print("Workflows:", workflows)
