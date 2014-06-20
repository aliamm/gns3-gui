# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Graphical representation of a note on the QGraphicsScene.
"""

from ..qt import QtCore, QtGui


class NoteItem(QtGui.QGraphicsTextItem):
    """
    Text note for the QGraphicsView.

    :param parent: optional parent
    """

    def __init__(self, parent=None):

        QtGui.QGraphicsTextItem.__init__(self, parent)
        self.setFont(QtGui.QFont("TypeWriter", 10, QtGui.QFont.Bold))
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemIsSelectable)
        self.setZValue(2)
        self._editable = True

    def delete(self):
        """
        Deletes this note.
        """

        self.scene().removeItem(self)
        from ..topology import Topology
        Topology.instance().removeNote(self)

    def editable(self):
        """
        Returns either the note is editable or not.

        :return: boolean
        """

        return self._editable

    def setEditable(self, value):
        """
        Sets the note has editable or not.

        :param value: boolean
        """

        self._editable = value

    def keyPressEvent(self, event):
        """
        Handles all key press events

        :param event: QKeyEvent
        """

        key = event.key()
        modifiers = event.modifiers()
        if key in (QtCore.Qt.Key_P, QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Plus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() > -360.0:
                self.setRotation(self.rotation() - 1)
        elif key in (QtCore.Qt.Key_M, QtCore.Qt.Key_Minus) and modifiers & QtCore.Qt.AltModifier \
                or key == QtCore.Qt.Key_Minus and modifiers & QtCore.Qt.AltModifier and modifiers & QtCore.Qt.KeypadModifier:
            if self.rotation() < 360.0:
                self.setRotation(self.rotation() + 1)
        else:
            QtGui.QGraphicsTextItem.keyPressEvent(self, event)

    def editText(self):
        """
        Edit mode for this note.
        """

        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setSelected(True)
        self.setFocus()
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.Document)
        self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event):
        """
        Handles all mouse double click events.

        :param event: QMouseEvent instance
        """

        if self._editable:
            self.editText()

    def focusOutEvent(self, event):
        """
        Handles all focus out events.

        :param event: QFocusEvent instance
        """

        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.clearSelection()
            self.setTextCursor(cursor)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        if not self.toPlainText():
            # delete the note if empty
            self.delete()
            return
        return QtGui.QGraphicsTextItem.focusOutEvent(self, event)

    #TODO: show layer position
    # def paint(self, painter, option, widget=None):
    #
    #     QtGui.QGraphicsTextItem.paint(self, painter, option, widget)
    #
    #     # Don't draw if not activated
    #     if globals.GApp.workspace.flg_showLayerPos == False:
    #         return
    #
    #     # Show layer level of this node
    #     brect = self.boundingRect()
    #
    #     # Don't draw if the object is too small ...
    #     if brect.width() < 20 or brect.height() < 20:
    #         return
    #
    #     center = self.mapFromItem(self, brect.width() / 2.0, brect.height() / 2.0)
    #
    #     painter.setBrush(QtCore.Qt.red)
    #     painter.setPen(QtCore.Qt.red)
    #     painter.drawRect((brect.width() / 2.0) - 10, (brect.height() / 2.0) - 10, 20, 20)
    #
    #     painter.setPen(QtCore.Qt.black)
    #     painter.setFont(QtGui.QFont("TypeWriter", 14, QtGui.QFont.Bold))
    #     zval = str(int(self.zValue()))
    #     painter.drawText(QtCore.QPointF(center.x() - 4, center.y() + 4), zval)

    def dump(self):
        """
        Returns a representation of this note.

        :returns: dictionary
        """

        note_info = {"text": self.toPlainText(),
                     "x": self.x(),
                     "y": self.y()}

        if self.font() != QtGui.QFont("TypeWriter", 10, QtGui.QFont.Bold):
            note_info["font"] = self.font().toString()
        if self.defaultTextColor() != QtCore.Qt.black:
            note_info["color"] = self.defaultTextColor().name()
        if self.rotation() != 0:
            note_info["rotation"] = self.rotation()
        if self.zValue() != 2:
            note_info["z"] = self.zValue()

        return note_info

    def load(self, note_info):
        """
        Loads a note representation
        (from a topology file).

        :param note_info: representation of the note (dictionary)
        """

        # load mandatory properties
        text = note_info["text"]
        x = note_info["x"]
        y = note_info["y"]

        self.setPlainText(text)
        self.setPos(x, y)

        # load optional properties
        font = note_info.get("font")
        color = note_info.get("color")
        rotation = note_info.get("rotation")
        z = note_info.get("z")

        if font:
            qt_font = QtGui.QFont()
            if qt_font.fromString(font):
                self.setFont(qt_font)
        if color:
            self.setDefaultTextColor(QtGui.QColor(color))
        if rotation is not None:
            self.setRotation(rotation)
        if z is not None:
            self.setZValue(z)

    def duplicate(self):
        """
        Duplicates this node item.

        :return: NoteItem instance
        """

        note_item = NoteItem(self.parent())
        note_item.setPlainText(self.toPlainText())
        note_item.setPos(self.x() + 20, self.y() + 20)
        note_item.setZValue(self.zValue())
        note_item.setFont(self.font())
        note_item.setDefaultTextColor(self.defaultTextColor())
        note_item.setRotation(self.rotation())
        return note_item
