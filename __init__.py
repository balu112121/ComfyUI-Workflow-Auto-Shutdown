from .nodes import WorkflowAutoShutdown, CancelScheduledShutdown

NODE_CLASS_MAPPINGS = {
    "WorkflowAutoShutdown": WorkflowAutoShutdown,
    "CancelScheduledShutdown": CancelScheduledShutdown
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowAutoShutdown": "工作流自动关机小助手",
    "CancelScheduledShutdown": "取消计划关机"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']