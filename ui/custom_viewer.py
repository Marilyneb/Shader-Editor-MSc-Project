from NodeGraphQt.widgets.viewer import NodeViewer

class CustomNodeViewer(NodeViewer):
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        pos = event.position()
        self._set_viewer_zoom(delta, pos=pos)
