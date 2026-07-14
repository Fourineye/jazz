from .. import Globals
from .sprite import Sprite
from ..engine.base_object import GameObject
from ..utils import Vec2, Color, Rect, Texture
from ..primatives import Draw

class UIContainer(Sprite):
    """Container component that groups, renders, and layouts child UI elements."""

    def __init__(self, name: str = "UIContainer", **kwargs) -> None:
        """Initializes the UIContainer component.

        Args:
            name (str, optional): The name of the layout container. Defaults to "UIContainer".
            padding (int | float | list | tuple, optional): Inner padding: single value, (vertical, horizontal), or (top, right, bottom, left). Defaults to 0.
            spacing (int | float, optional): Space between children. Defaults to 0.
            layout_type (str, optional): Layout policy: "none", "vertical", or "horizontal". Defaults to "none".
            align (str, optional): Cross-axis alignment: "start", "center", "end" or equivalent. Defaults to "start".
            auto_size (bool, optional): Adjust container size to wrap children. Defaults to True if no size is specified.
            size (Vec2 | tuple, optional): Explicit width and height bounds.
            texture (str | Texture | Surface, optional): Optional background rendering asset.
            bg_color (tuple | Color, optional): Background fill color. Defaults to None.
            radius (int, optional): Corner rounding radius for the background. Defaults to 6.
            style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "flat".
            shadow_offset (tuple, optional): X and Y offset for the drop shadow. Defaults to (2, 4).
            shadow_color (tuple | Color, optional): Color of the drop shadow. Defaults to black with alpha 60.
            shadow_blur (int, optional): Soft blur step size of the drop shadow. Defaults to 4.
            border_color (tuple | Color, optional): Border outline color. Defaults to None.
            border_width (int, optional): Border stroke thickness. Defaults to 0.
        """
        self.padding = kwargs.get("padding", 0)
        self.spacing = kwargs.get("spacing", 0)
        self.layout_type = kwargs.get("layout_type", "none").lower()
        self.align = kwargs.get("align", kwargs.get("cross_align", "start")).lower()
        
        self.bg_color = kwargs.get("bg_color", None)
        self._has_background = "texture" in kwargs or self.bg_color is not None
        self._kwargs = kwargs.copy()
        
        # Default UI container layout anchor to top-left (0, 0) for intuitive positioning
        kwargs.setdefault("anchor", (0, 0))
        
        super().__init__(name, **kwargs)
        
        if "size" in kwargs:
            self._size = Vec2(kwargs["size"])
            self._hardware_offset()
            self.auto_size = kwargs.get("auto_size", False)
            if self.bg_color is not None and "texture" not in kwargs:
                radius = kwargs.get("radius", 6)
                style = kwargs.get("style", "flat")
                shadow_offset = kwargs.get("shadow_offset", (2, 4))
                shadow_color = kwargs.get("shadow_color", (0, 0, 0, 60))
                shadow_blur = kwargs.get("shadow_blur", 4)
                border_color = kwargs.get("border_color", None)
                border_width = kwargs.get("border_width", 0)
                
                self.texture = Globals.resource.get_styled_texture(
                    self._size, self.bg_color, radius, shadow_offset, shadow_color, shadow_blur, style, border_color, border_width
                )
        else:
            if not self._has_background:
                self._size = Vec2(0, 0)
                self._hardware_offset()
            self.auto_size = kwargs.get("auto_size", True)

    @property
    def size(self) -> Vec2:
        """Vec2: Gets the size of the container."""
        return Vec2(self._size)

    @size.setter
    def size(self, new_size: Vec2 | tuple[float, float]) -> None:
        """Sets the size of the container.

        Args:
            new_size (Vec2 | tuple): The new dimensions of the container.
        """
        self._size = Vec2(new_size)
        self._hardware_offset()

    def _parse_padding(self) -> tuple[float, float, float, float]:
        """Parses padding into a 4-tuple representing (top, right, bottom, left).

        Returns:
            tuple[float, float, float, float]: Top, right, bottom, and left padding values.
        """
        padding = self.padding
        if isinstance(padding, (int, float)):
            return (padding, padding, padding, padding)
        elif isinstance(padding, (tuple, list)):
            if len(padding) == 2:
                return (padding[1], padding[0], padding[1], padding[0])
            elif len(padding) == 4:
                return tuple(padding)
        return (0.0, 0.0, 0.0, 0.0)

    def _get_child_size(self, child: GameObject) -> Vec2:
        """Calculates the size of a child component, accounting for scale.

        Args:
            child (GameObject): The child game object.

        Returns:
            Vec2: Calculated size of the child component.
        """
        size = Vec2(0, 0)
        if hasattr(child, "_size"):
            size = Vec2(child._size)
        elif hasattr(child, "size"):
            size = Vec2(child.size)
        
        scale = Vec2(1, 1)
        if hasattr(child, "_scale"):
            scale = Vec2(child._scale)
        elif hasattr(child, "scale"):
            scale = Vec2(child.scale)
        return size.elementwise() * scale

    def _get_child_draw_offset(self, child: GameObject) -> Vec2:
        """Retrieves the local draw offset of a child component.

        Args:
            child (GameObject): The child game object.

        Returns:
            Vec2: Draw offset of the child.
        """
        if hasattr(child, "_draw_offset"):
            return Vec2(child._draw_offset)
        return Vec2(0, 0)

    @property
    def local_top_left(self) -> Vec2:
        """Gets the top-left offset coordinate in local space relative to parent origin.

        Returns:
            Vec2: The top-left local coordinate.
        """
        if hasattr(self, "_draw_offset"):
            return Vec2(self._draw_offset)
        return Vec2(0, 0)

    def layout(self) -> None:
        """Arranges the direct visible children of this container based on the layout policy.
        
        Updates the size of the container if auto_size is enabled.
        """
        old_size = Vec2(self._size)
        children = [c for c in self._children.values() if getattr(c, "_visible", True)]
        if not children:
            if self.auto_size:
                self._size = Vec2(0, 0)
                self._hardware_offset()
            if self.bg_color is not None:
                self.texture = None
            return

        top, right, bottom, left = self._parse_padding()
        child_sizes = [self._get_child_size(c) for c in children]
        
        if self.layout_type == "vertical":
            max_w = max(sz.x for sz in child_sizes)
            sum_h = sum(sz.y for sz in child_sizes)
            
            if self.auto_size:
                container_w = left + max_w + right
                container_h = top + sum_h + self.spacing * (len(children) - 1) + bottom
                self._size = Vec2(container_w, max(0, container_h))
                self._hardware_offset()
            else:
                container_w = self._size.x
                max_w = container_w - left - right
                container_h = self._size.y
            
            current_y = self.local_top_left.y + top
            for child, c_size in zip(children, child_sizes):
                c_offset = self._get_child_draw_offset(child)
                
                if self.align in ["start", "left"]:
                    target_x = self.local_top_left.x + left
                elif self.align in ["center", "middle"]:
                    target_x = self.local_top_left.x + left + (max_w - c_size.x) / 2
                elif self.align in ["end", "right"]:
                    target_x = self.local_top_left.x + container_w - right - c_size.x
                else:
                    target_x = self.local_top_left.x + left

                child.local_pos = Vec2(target_x, current_y) - c_offset
                current_y += c_size.y + self.spacing
                
        elif self.layout_type == "horizontal":
            sum_w = sum(sz.x for sz in child_sizes)
            max_h = max(sz.y for sz in child_sizes)
            
            if self.auto_size:
                container_w = left + sum_w + self.spacing * (len(children) - 1) + right
                container_h = top + max_h + bottom
                self._size = Vec2(max(0, container_w), container_h)
                self._hardware_offset()
            else:
                container_w = self._size.x
                container_h = self._size.y
                max_h = container_h - top - bottom
                
            current_x = self.local_top_left.x + left
            for child, c_size in zip(children, child_sizes):
                c_offset = self._get_child_draw_offset(child)
                
                if self.align in ["start", "top"]:
                    target_y = self.local_top_left.y + top
                elif self.align in ["center", "middle"]:
                    target_y = self.local_top_left.y + top + (max_h - c_size.y) / 2
                elif self.align in ["end", "bottom"]:
                    target_y = self.local_top_left.y + container_h - bottom - c_size.y
                else:
                    target_y = self.local_top_left.y + top

                child.local_pos = Vec2(current_x, target_y) - c_offset
                current_x += c_size.x + self.spacing

        elif self.layout_type == "none":
            if self.auto_size:
                min_x = min_y = float('inf')
                max_x = max_y = float('-inf')
                for child, c_size in zip(children, child_sizes):
                    c_pos = child.local_pos + self._get_child_draw_offset(child)
                    min_x = min(min_x, c_pos.x)
                    min_y = min(min_y, c_pos.y)
                    max_x = max(max_x, c_pos.x + c_size.x)
                    max_y = max(max_y, c_pos.y + c_size.y)
                
                if min_x != float('inf'):
                    self._size = Vec2(max_x - min_x + left + right, max_y - min_y + top + bottom)
                    self._hardware_offset()
                else:
                    self._size = Vec2(0, 0)
                    self._hardware_offset()

        # If size changed and we have a dynamic background color, regenerate it:
        if self.bg_color is not None and (self._size != old_size or self.texture is None):
            if self._size.x == 0 or self._size.y == 0:
                self.texture = None
            else:
                radius = self._kwargs.get("radius", 6)
                style = self._kwargs.get("style", "flat")
                shadow_offset = self._kwargs.get("shadow_offset", (2, 4))
                shadow_color = self._kwargs.get("shadow_color", (0, 0, 0, 60))
                shadow_blur = self._kwargs.get("shadow_blur", 4)
                border_color = self._kwargs.get("border_color", None)
                border_width = self._kwargs.get("border_width", 0)
                
                self.texture = Globals.resource.get_styled_texture(
                    self._size, self.bg_color, radius, shadow_offset, shadow_color, shadow_blur, style, border_color, border_width
                )

    def add_child(self, obj: GameObject) -> GameObject:
        """Adds a child object to the container and triggers layout update.

        Args:
            obj (GameObject): The child game object to add.

        Returns:
            GameObject: The added game object.
        """
        res = super().add_child(obj)
        self.layout()
        return res

    def remove_child(self, obj: GameObject, kill: bool = True) -> None:
        """Removes a child object from the container and triggers layout update.

        Args:
            obj (GameObject): The child game object to remove.
            kill (bool, optional): Destroy the child object. Defaults to True.
        """
        super().remove_child(obj, kill=kill)
        self.layout()

    def update(self, delta: float) -> None:
        """Updates layout and propagates updates.

        Args:
            delta (float): The time delta in seconds since the last frame.
        """
        super().update(delta)
        self.layout()

    @property
    def texture(self):
        """Texture | Image: Gets the active Texture or Image asset."""
        return self._texture

    @texture.setter
    def texture(self, new_texture) -> None:
        """Sets the texture asset, preserving the logical size of the container."""
        logical_size = Vec2(self._size) if hasattr(self, "_size") else None
        Sprite.texture.fset(self, new_texture)
        if self.bg_color is not None and logical_size is not None:
            self._size = logical_size
            self._hardware_offset()

    def render(self, offset: Vec2) -> None:
        """Draws the background texture onto the screen if a custom texture is registered.

        Args:
            offset (Vec2): Viewport rendering offset to apply.
        """
        if not self._has_background or self.texture is None:
            return
            
        if self.bg_color is not None and hasattr(self, "_kwargs"):
            shadow_offset = self._kwargs.get("shadow_offset", (2, 4))
            shadow_blur = self._kwargs.get("shadow_blur", 4)
            pad_x = abs(shadow_offset[0]) + shadow_blur * 2
            pad_y = abs(shadow_offset[1]) + shadow_blur * 2
            
            dest_pos = self.draw_pos + offset - Vec2(pad_x, pad_y).elementwise() * self._scale
            dest_size = Vec2(self.texture.width, self.texture.height).elementwise() * self._scale
            dest = Rect(dest_pos, dest_size)
            
            if isinstance(self.texture, Texture):
                origin = -self._draw_offset + Vec2(pad_x, pad_y).elementwise() * self._scale
                self.texture.draw(
                    None,
                    dest,
                    self.rotation,
                    origin,
                    self.flip_x,
                    self.flip_y,
                )
            else:
                self.texture.flip_x = self.flip_x
                self.texture.flip_y = self.flip_y
                self.texture.angle = -self.rotation
                self.texture.alpha = self._alpha
                self.texture.draw(None, dest)
        else:
            super().render(offset)

    def render_debug(self, offset: Vec2) -> None:
        """Draws the boundaries of the container and its padding regions in debug mode.

        Args:
            offset (Vec2): Screen space render offset.
        """
        super().render_debug(offset)
        
        outer_rect = self.rect.move(offset)
        Draw.rect(outer_rect, Color("red"), 2)
        
        top, right, bottom, left = self._parse_padding()
        inner_rect = Rect(
            outer_rect.x + left,
            outer_rect.y + top,
            max(0, outer_rect.width - left - right),
            max(0, outer_rect.height - top - bottom)
        )
        Draw.rect(inner_rect, Color("orange"), 1)

    def debug_draw(self, offset: Vec2) -> None:
        """Alias for render_debug for user convenience.

        Args:
            offset (Vec2): Screen space render offset.
        """
        self.render_debug(offset)


class VBox(UIContainer):
    """Vertical box layout container component."""

    def __init__(self, name: str = "VBox", **kwargs) -> None:
        """Initializes the VBox component.

        Args:
            name (str, optional): The name of the layout container. Defaults to "VBox".
            padding (int | float | list | tuple, optional): Inner padding. Defaults to 5.
            spacing (int | float, optional): Space between children. Defaults to 5.
            align (str, optional): Horizontal alignment: "left", "center", "right". Defaults to "center".
            auto_size (bool, optional): Adjust container size to wrap children. Defaults to True if no size is specified.
            size (Vec2 | tuple, optional): Explicit width and height bounds.
            texture (str | Texture | Surface, optional): Optional background rendering asset.
            bg_color (tuple | Color, optional): Background fill color. Defaults to None.
            radius (int, optional): Corner rounding radius for the background. Defaults to 6.
            style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "flat".
            shadow_offset (tuple, optional): X and Y offset for the drop shadow. Defaults to (2, 4).
            shadow_color (tuple | Color, optional): Color of the drop shadow. Defaults to black with alpha 60.
            shadow_blur (int, optional): Soft blur step size of the drop shadow. Defaults to 4.
            border_color (tuple | Color, optional): Border outline color. Defaults to None.
            border_width (int, optional): Border stroke thickness. Defaults to 0.
        """
        kwargs.setdefault("layout_type", "vertical")
        kwargs.setdefault("align", "center")
        kwargs.setdefault("padding", 5)
        kwargs.setdefault("spacing", 5)
        super().__init__(name, **kwargs)


class HBox(UIContainer):
    """Horizontal box layout container component."""

    def __init__(self, name: str = "HBox", **kwargs) -> None:
        """Initializes the HBox component.

        Args:
            name (str, optional): The name of the layout container. Defaults to "HBox".
            padding (int | float | list | tuple, optional): Inner padding. Defaults to 5.
            spacing (int | float, optional): Space between children. Defaults to 5.
            align (str, optional): Vertical alignment: "top", "center", "bottom". Defaults to "center".
            auto_size (bool, optional): Adjust container size to wrap children. Defaults to True if no size is specified.
            size (Vec2 | tuple, optional): Explicit width and height bounds.
            texture (str | Texture | Surface, optional): Optional background rendering asset.
            bg_color (tuple | Color, optional): Background fill color. Defaults to None.
            radius (int, optional): Corner rounding radius for the background. Defaults to 6.
            style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "flat".
            shadow_offset (tuple, optional): X and Y offset for the drop shadow. Defaults to (2, 4).
            shadow_color (tuple | Color, optional): Color of the drop shadow. Defaults to black with alpha 60.
            shadow_blur (int, optional): Soft blur step size of the drop shadow. Defaults to 4.
            border_color (tuple | Color, optional): Border outline color. Defaults to None.
            border_width (int, optional): Border stroke thickness. Defaults to 0.
        """
        kwargs.setdefault("layout_type", "horizontal")
        kwargs.setdefault("align", "center")
        kwargs.setdefault("padding", 5)
        kwargs.setdefault("spacing", 5)
        super().__init__(name, **kwargs)
