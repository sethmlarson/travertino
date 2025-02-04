from unittest import TestCase

from travertino.declaration import BaseStyle
from travertino.layout import BaseBox, Viewport
from travertino.node import Node
from travertino.size import BaseIntrinsicSize


class Style(BaseStyle):
    class IntrinsicSize(BaseIntrinsicSize):
        pass

    class Box(BaseBox):
        pass

    def layout(self, root, viewport):
        # A simple layout scheme that allocats twice the viewport size.
        root.layout.content_width = viewport.width * 2
        root.layout.content_height = viewport.height * 2


class NodeTests(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_create_leaf(self):
        "A leaf can be created"
        style = Style()
        leaf = Node(style=style)

        self.assertIsNone(leaf._children)
        self.assertEqual(leaf.children, [])
        self.assertFalse(leaf.can_have_children)

        # An unattached leaf is a root
        self.assertIsNone(leaf.parent)
        self.assertEqual(leaf.root, leaf)

        # A leaf can't have children
        child = Node(style=style)

        with self.assertRaises(ValueError):
            leaf.add(child)

    def test_create_node(self):
        "A node can be created with children"
        style = Style()

        child1 = Node(style=style)
        child2 = Node(style=style)
        child3 = Node(style=style)

        node = Node(style=style, children=[child1, child2, child3])

        self.assertEqual(node.children, [child1, child2, child3])
        self.assertTrue(node.can_have_children)

        # The node is the root as well.
        self.assertIsNone(node.parent)
        self.assertEqual(node.root, node)

        # The children all point at the node.
        self.assertEqual(child1.parent, node)
        self.assertEqual(child1.root, node)

        self.assertEqual(child2.parent, node)
        self.assertEqual(child2.root, node)

        self.assertEqual(child3.parent, node)
        self.assertEqual(child3.root, node)

        # Create another node
        new_node = Node(style=style, children=[])

        self.assertEqual(new_node.children, [])
        self.assertTrue(new_node.can_have_children)

        # Add the old node as a child of the new one.
        new_node.add(node)

        # The new node is the root
        self.assertIsNone(new_node.parent)
        self.assertEqual(new_node.root, new_node)

        # The node is the root as well.
        self.assertEqual(node.parent, new_node)
        self.assertEqual(node.root, new_node)

        # The children all point at the node.
        self.assertEqual(child1.parent, node)
        self.assertEqual(child1.root, new_node)

        self.assertEqual(child2.parent, node)
        self.assertEqual(child2.root, new_node)

        self.assertEqual(child3.parent, node)
        self.assertEqual(child3.root, new_node)

    def test_refresh(self):
        "The layout can be refreshed, and the applicator invoked"

        # Define an applicator that tracks the node being rendered and it's size
        class Applicator:
            def __init__(self, node):
                self.tasks = []
                self.node = node

            def set_bounds(self):
                self.tasks.append(
                    (
                        self.node,
                        self.node.layout.content_width,
                        self.node.layout.content_height,
                    )
                )

        class TestNode(Node):
            def __init__(self, style, children=None):
                super().__init__(
                    style=style, applicator=Applicator(self), children=children
                )

        # Define a simple 2 level tree of nodes.
        style = Style()
        child1 = TestNode(style=style)
        child2 = TestNode(style=style)
        child3 = TestNode(style=style)

        node = TestNode(style=style, children=[child1, child2, child3])

        # Refresh the root node
        node.refresh(Viewport(width=10, height=20))

        # Check the output is as expected
        self.assertEqual(node.applicator.tasks, [(node, 20, 40)])
        self.assertEqual(child1.applicator.tasks, [])
        self.assertEqual(child2.applicator.tasks, [])
        self.assertEqual(child3.applicator.tasks, [])

        # Reset the applicator
        node.applicator.tasks = []

        # Refresh a child node
        child1.refresh(Viewport(width=15, height=25))

        # The root node was rendered, not the child.
        self.assertEqual(node.applicator.tasks, [(node, 30, 50)])
        self.assertEqual(child1.applicator.tasks, [])
        self.assertEqual(child2.applicator.tasks, [])
        self.assertEqual(child3.applicator.tasks, [])

    def test_add(self):
        "Nodes can be added as children to another node"

        style = Style()
        node = Node(style=style, children=[])

        child = Node(style=style)
        node.add(child)

        self.assertTrue(child in node.children)
        self.assertEqual(child.parent, node)
        self.assertEqual(child.root, node.root)

    def test_insert(self):
        "Node can be inserted at a specific position as a child"

        style = Style()
        child1 = Node(style=style)
        child2 = Node(style=style)
        child3 = Node(style=style)
        node = Node(style=style, children=[child1, child2, child3])

        child4 = Node(style=style)

        index = 2
        node.insert(index, child4)

        self.assertTrue(child4 in node.children)
        self.assertEqual(child4.parent, node)
        self.assertEqual(child4.root, node.root)

        self.assertEqual(node.children.index(child4), index)

    def test_remove(self):
        "Children can be removed from node"

        style = Style()
        child1 = Node(style=style)
        child2 = Node(style=style)
        child3 = Node(style=style)
        node = Node(style=style, children=[child1, child2, child3])

        node.remove(child1)

        self.assertFalse(child1 in node.children)
        self.assertEqual(child1.parent, None)
        self.assertEqual(child1.root, child1)

    def test_clear(self):
        "Node can be inserted at a specific position as a child"
        style = Style()
        children = [Node(style=style), Node(style=style), Node(style=style)]
        node = Node(style=style, children=children)

        for child in children:
            self.assertTrue(child in node.children)
            self.assertEqual(child.parent, node)
            self.assertEqual(child.root, node)
        self.assertEqual(node.children, children)

        node.clear()

        for child in children:
            self.assertFalse(child in node.children)
            self.assertEqual(child.parent, None)
            self.assertEqual(child.root, child)

        self.assertEqual(node.children, [])
