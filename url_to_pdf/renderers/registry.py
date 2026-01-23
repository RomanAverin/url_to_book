from typing import Type, TypeVar

from .base import BaseRenderer

T = TypeVar("T", bound=BaseRenderer)


class RendererRegistry:
    """Singleton registry for renderer classes."""

    _instance: "RendererRegistry | None" = None
    _renderers: dict[str, Type[BaseRenderer]]

    def __new__(cls) -> "RendererRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._renderers = {}
        return cls._instance

    def register(self, cls: Type[T]) -> Type[T]:
        """Decorator to register a renderer class."""
        instance = cls()
        self._renderers[instance.format_name] = cls
        return cls

    def get(self, format_name: str) -> Type[BaseRenderer]:
        """Get renderer class by format name."""
        if format_name not in self._renderers:
            available = ", ".join(self._renderers.keys())
            raise ValueError(
                f"Unknown format '{format_name}'. Available formats: {available}"
            )
        return self._renderers[format_name]

    def create(self, format_name: str, **kwargs) -> BaseRenderer:
        """Create renderer instance by format name."""
        renderer_cls = self.get(format_name)
        return renderer_cls(**kwargs)

    def list_formats(self) -> list[str]:
        """List all registered format names."""
        return list(self._renderers.keys())


registry = RendererRegistry()


def get_renderer(format_name: str, **kwargs) -> BaseRenderer:
    """Create renderer instance by format name."""
    return registry.create(format_name, **kwargs)


def list_formats() -> list[str]:
    """List all registered format names."""
    return registry.list_formats()
