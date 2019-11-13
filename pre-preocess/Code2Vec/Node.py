class Node:
    def __init__(self, id, content):
        self.children = []
        self.id = id
        self.content = content
        self.parent = []

    def add_child(self, child_node_id):
        if child_node_id not in self.children:
            self.children.append(child_node_id)

    def has_child(self, child_node):
        if child_node.get_id() in self.children:
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def add_parent(self, parent_id):
        if parent_id not in self.parent:
            self.parent.append(parent_id)

    def get_content(self):
        return self.content

    def set_content(self, content):
        self.content = content

    def get_children(self):
        if len(self.children) == 0:
            self.children.append(-1)
        return self.children

    def get_parent(self):
        if len(self.parent) == 0:
            self.parent.append(-1)
        return self.parent
