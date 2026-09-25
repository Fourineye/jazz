"""
Serialization and Deserialization module for Jazz Engine.

Provides class registration, modular resource loading, and scene/object JSON factory methods.
"""

import importlib
import inspect
import json
import os
from collections.abc import Callable
from typing import Any, ClassVar, TypeVar

from ..global_dict import Globals
from ..utils import JazzException

T = TypeVar("T")


def _accepts_name(target_cls: type) -> bool:
    """Checks whether a class constructor accepts a `name` keyword argument.

    Args:
        target_cls (type): The class to inspect.

    Returns:
        bool: True if `__init__` has a `name` parameter or takes `**kwargs`.
    """
    try:
        params = inspect.signature(target_cls.__init__).parameters
    except (TypeError, ValueError):
        return True
    return "name" in params or any(
        p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()
    )


class Serializer:
    """Registry and serialization engine for game objects, scenes, and resources."""

    _class_registry: ClassVar[dict[str, type]] = {}
    _resource_handlers: ClassVar[dict[str, Callable[[dict[str, Any]], Any]]] = {}

    @classmethod
    def register_class(cls, target_cls: type[T]) -> type[T]:
        """Registers a Python class for dynamic deserialization by class name.

        Can be used as a decorator `@register_class` or called directly `Serializer.register_class(MyClass)`.

        Args:
            target_cls (Type[T]): The class to register.

        Returns:
            Type[T]: The registered class for decorator chaining.
        """
        class_name = target_cls.__name__
        cls._class_registry[class_name] = target_cls
        return target_cls

    @classmethod
    def get_class(cls, class_name: str) -> type:
        """Retrieves a registered Python class by name.

        Args:
            class_name (str): The name of the registered class.

        Returns:
            Type: The registered class.

        Raises:
            JazzException: If the class is not registered.
        """
        target = cls._class_registry.get(class_name, None)
        if target is None:
            raise JazzException(f"Unregistered class '{class_name}'. Ensure it is registered using @register_class or Serializer.register_class().")
        return target

    @classmethod
    def register_resource_handler(cls, type_name: str, handler_func: Callable[[dict[str, Any]], Any]) -> None:
        """Registers a custom handler function for a resource type in JSON definitions.

        Args:
            type_name (str): The resource type identifier (e.g. "texture", "animation").
            handler_func (Callable[[dict], Any]): Function taking a resource dictionary and returning/storing the asset.
        """
        cls._resource_handlers[type_name] = handler_func

    @classmethod
    def resolve_script(cls, script_path: str) -> Callable[..., Any]:
        """Imports and resolves a python function or callable from a dot-separated string.

        Args:
            script_path (str): Fully-qualified function path (e.g., 'my_module.scripts.on_player_update').

        Returns:
            Callable: The resolved callable function object.

        Raises:
            JazzException: If the module or attribute cannot be resolved.
        """
        if "." not in script_path:
            raise JazzException(f"Invalid script path '{script_path}'. Must be in 'module.function' format.")
        module_path, func_name = script_path.rsplit(".", 1)
        try:
            mod = importlib.import_module(module_path)
            func = getattr(mod, func_name)
            return func
        except Exception as e:
            raise JazzException(f"Failed to resolve script '{script_path}': {e}") from e

    @classmethod
    def process_resources(cls, resources: list[str | dict[str, Any]], base_path: str = "") -> None:
        """Processes a list of resource declarations or external resource JSON file paths.

        Args:
            resources (list[str | dict]): List of resource dicts or file paths to load.
            base_path (str, optional): Base path folder for resolving relative resource JSON paths. Defaults to "".
        """
        for item in resources:
            if isinstance(item, str):
                file_path = os.path.join(base_path, item) if base_path else item
                if not os.path.exists(file_path):
                    raise JazzException(f"Resource JSON file not found: '{file_path}'")
                with open(file_path, "r", encoding="utf-8") as f:
                    external_resources = json.load(f)
                if isinstance(external_resources, list):
                    dir_path = os.path.dirname(file_path)
                    cls.process_resources(external_resources, base_path=dir_path)
            elif isinstance(item, dict):
                res_type = item.get("type", None)
                if res_type is None:
                    raise JazzException("Resource entry missing required 'type' field.")
                handler = cls._resource_handlers.get(res_type, None)
                if handler is not None:
                    handler(item)
                else:
                    res_id = item.get("id", "unnamed")
                    Globals.resource.add_resource(res_type, res_id, item)

    #TODO: Implement live value Serialization for save states
    @classmethod
    def serialize_object(cls, obj: Any) -> dict[str, Any]:
        """Serializes an object and its children into a dictionary payload.

        Children added by the object's own constructor are skipped, since the
        constructor creates them again when the object is loaded.

        Args:
            obj (Any): The object to serialize.

        Returns:
            dict[str, Any]: Dict representation of the object.
        """
        from ..utils import Vec2
        raw_options = obj._kwargs.copy() if getattr(obj, "_kwargs", None) else {}
        options: dict[str, Any] = {}
        for k, v in raw_options.items():
            if isinstance(v, Vec2):
                options[k] = [float(v.x), float(v.y)]
            elif isinstance(v, (list, tuple)):
                options[k] = [list(item) if isinstance(item, Vec2) else item for item in v]
            else:
                options[k] = v

        options["name"] = getattr(obj, "name", getattr(obj, "id", "Object"))

        children = getattr(obj, "_children", {})
        if isinstance(children, dict) and children:
            children_list = [
                cls.serialize_object(child)
                for child in children.values()
                if not getattr(child, "_internal", False)
            ]
        else:
            children_list = []

        props = getattr(obj, "properties", getattr(obj, "_properties", {}))
        props_dict = dict(props) if isinstance(props, dict) else {}

        # Only script paths can be serialized; callables assigned at runtime are skipped
        scripts = {
            hook: path
            for hook, path in getattr(obj, "_scripts", {}).items()
            if isinstance(path, str)
        }

        return {
            "Class": obj.__class__.__name__,
            "options": options,
            "properties": props_dict,
            "scripts": scripts,
            "children": children_list,
        }

    @classmethod
    def make_script_wrapper(cls, obj: Any, fn: Any) -> Any:
        """Wraps a resolved script function to automatically supply instance context if required by signature.

        Args:
            obj (Any): Target instance object context.
            fn (Any): Function or callable to wrap.

        Returns:
            Any: Wrapped function or original asset.
        """
        if not callable(fn):
            return fn
        import inspect
        try:
            sig = inspect.signature(fn)
            num_params = len(sig.parameters)
        except (ValueError, TypeError):
            return fn

        def wrapper(*args, **kwargs):
            if num_params == 0:
                return fn()
            if len(args) < num_params:
                return fn(obj, *args, **kwargs)
            return fn(*args, **kwargs)

        return wrapper

    @classmethod
    def deserialize_object(cls, data: dict[str, Any], target_cls: type | None = None) -> Any:
        """Instantiates and restores a GameObject hierarchy from a dictionary payload.

        The name is passed to the constructor when it accepts one; otherwise it is
        assigned after construction. Errors raised by the constructor propagate.

        Args:
            data (dict[str, Any]): Dict payload containing object properties.
            target_cls (type, optional): Specific class to instantiate. Defaults to None.

        Returns:
            Any: The instantiated object.
        """
        if target_cls is None:
            class_name = data.get("Class", "GameObject")
            target_cls = cls.get_class(class_name)

        options = dict(data.get("options", {}))
        name = options.pop("name", "Object")
        scripts = data.get("scripts", options.pop("scripts", None))

        if _accepts_name(target_cls):
            obj = target_cls(name=name, **options)
        else:
            obj = target_cls(**options)
            if hasattr(obj, "name"):
                obj.name = name

        if isinstance(scripts, dict):
            for hook, script_path in scripts.items():
                if hasattr(obj, "assign_script"):
                    # Pass the raw path so it is kept in _scripts for re-serialization
                    obj.assign_script(hook, script_path)
                else:
                    resolved_script = cls.resolve_script(script_path) if isinstance(script_path, str) else script_path
                    setattr(obj, hook, cls.make_script_wrapper(obj, resolved_script))

        children = data.get("children", [])
        for child_data in children:
            child_obj = cls.deserialize_object(child_data)
            obj.add_child(child_obj)

        return obj

    @classmethod
    def serialize_scene(cls, scene: Any) -> dict[str, Any]:
        """Serializes a Scene and its root game object graph into a dictionary payload.

        Args:
            scene (Scene): The active scene instance to serialize.

        Returns:
            dict[str, Any]: Dict representation of the scene.
        """
        return scene.to_dict()

    @classmethod
    def deserialize_scene(cls, data: dict[str, Any], base_path: str = "") -> type:
        """Generates a dynamic Scene subclass that initializes resources, properties, scripts, and objects in its __init__.

        Args:
            data (dict[str, Any]): Dict payload containing scene properties, resources, and objects.
            base_path (str, optional): Directory path for resolving relative file locations. Defaults to "".

        Returns:
            type: Generated Scene subclass object.
        """
        scene_class_name = data.get("SceneClass", "Scene")
        base_scene_cls = cls.get_class(scene_class_name)
        scene_name = data.get("name", getattr(base_scene_cls, "name", "GeneratedScene"))

        def __init__(self_scene, *args, **kwargs):
            super(DynamicScene, self_scene).__init__(*args, **kwargs)
            self_scene.name = scene_name

            resources = data.get("Resources", [])
            if resources:
                Serializer.process_resources(resources, base_path=base_path)

            props = data.get("properties", data.get("options", {}))
            if isinstance(props, dict):
                self_scene.properties = dict(props)
                for k, v in props.items():
                    if hasattr(self_scene, k):
                        setattr(self_scene, k, v)

            objects = data.get("Objects", [])
            old_scene = Globals.scene
            Globals.scene = self_scene
            try:
                for obj_data in objects:
                    obj = Serializer.deserialize_object(obj_data)
                    self_scene.add_object(obj)
            finally:
                Globals.scene = old_scene

        DynamicScene = type(
            str(scene_name),
            (base_scene_cls,),
            {
                "__module__": __name__,
                "__init__": __init__,
                "name": scene_name,
                "scene_data": data,
                "base_path": base_path,
            },
        )

        scripts = data.get("scripts", None)
        if isinstance(scripts, dict):
            DynamicScene.scripts = dict(scripts)
            for hook, script_path in scripts.items():
                if isinstance(script_path, str):
                    func = Serializer.resolve_script(script_path)
                    def make_wrapper(fn):
                        def wrapper(*a, **kw):
                            return fn(*a, **kw)
                        return wrapper
                    setattr(DynamicScene, hook, make_wrapper(func))

        return DynamicScene


def register_class(target_cls: type[T]) -> type[T]:
    """Decorator helper for registering classes with Serializer.

    Args:
        target_cls (Type[T]): Class to register.

    Returns:
        Type[T]: The registered class.
    """
    return Serializer.register_class(target_cls)


# Default built-in resource handlers
def _handle_texture(data: dict[str, Any]) -> Any:
    """Resource handler function for texture resource declarations.

    Args:
        data (dict[str, Any]): Texture resource configuration dictionary.

    Returns:
        Any: Loaded texture or None.

    Raises:
        JazzException: If the declaration has no `path`.
    """
    path = data.get("path")
    if not path:
        raise JazzException("Texture resource entry missing required 'path' field.")
    res_id = data.get("id", path)
    if Globals.resource is not None:
        tex = Globals.resource.get_texture(path)
        if res_id and res_id != path:
            Globals.resource.add_texture(tex, res_id, force=True)
        return tex
    return None


def _handle_sprite_sheet(data: dict[str, Any]) -> Any:
    """Resource handler function for spritesheet resource declarations.

    Args:
        data (dict[str, Any]): Spritesheet resource configuration dictionary.

    Returns:
        Any: Sliced spritesheet frame list or None.
    """
    path = data.get("path") or data.get("id")
    dim = data.get("sprite_dim", (0, 0))
    offset = data.get("sprite_offset", (0, 0))
    spacing = data.get("sprite_spacing", (0, 0))
    if Globals.resource is not None and path:
        sheet = Globals.resource.make_sprite_sheet(path, dim, offset, spacing)
        res_id = data.get("id")
        if res_id and res_id != path:
            Globals.resource._sprite_sheets[res_id] = sheet
        return sheet
    return None


def _handle_animation(data: dict[str, Any]) -> Any:
    """Resource handler function for animation resource declarations.

    Args:
        data (dict[str, Any]): Animation resource configuration dictionary.

    Returns:
        Any: Registered animation resource dictionary or None.

    Raises:
        JazzException: If the declaration has no `id` or `spritesheet`.
    """
    res_id = data.get("id")
    sheet = data.get("spritesheet")
    if not res_id or not sheet:
        raise JazzException("Animation resource entry requires 'id' and 'spritesheet' fields.")
    frames = data.get("animation_frames", None)
    fps = data.get("animation_fps", 30)
    oneshot = data.get("oneshot", False)
    if Globals.resource is not None:
        return Globals.resource.add_animation_resource(res_id, sheet, frames, fps, oneshot)
    return None


def _handle_sound(data: dict[str, Any]) -> Any:
    """Resource handler function for sound resource declarations.

    Args:
        data (dict[str, Any]): Sound resource configuration dictionary.

    Returns:
        Any: Loaded Sound object or None.
    """
    path = data.get("path")
    res_id = data.get("id", path)
    if Globals.sound is not None and path:
        return Globals.sound.load_sound(path, res_id)
    return None


def _handle_font(data: dict[str, Any]) -> Any:
    """Resource handler function for font resource declarations.

    Args:
        data (dict[str, Any]): Font resource configuration dictionary.

    Returns:
        Any: Loaded Font object or None.
    """
    path = data.get("path", data.get("name"))
    size = data.get("size", 12)
    if Globals.resource is not None and path:
        return Globals.resource.get_font(path, size)
    return None


Serializer.register_resource_handler("texture", _handle_texture)
Serializer.register_resource_handler("sprite_sheet", _handle_sprite_sheet)
Serializer.register_resource_handler("animation", _handle_animation)
Serializer.register_resource_handler("sound", _handle_sound)
Serializer.register_resource_handler("font", _handle_font)
