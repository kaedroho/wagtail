from treebeard.mp_tree import MP_Node


class Menu(MP_Node):
    label = models.CharField(max_length=50)
    # TODO: link fields

    max_depth = 1

    def __str__(self):
        return self.label

    class Meta:
        abstract = True

    # Rendering

    def render_self(self):
        return self.label

    def render_children(self):
        children = list(self.get_children())

        if children:
            return ''.join([child.render() for child in children])

    def render(self):
        return self.render_self() + self.render_children()
