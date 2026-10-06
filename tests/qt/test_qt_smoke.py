from PySide6.QtWidgets import QLabel, QWidget


def test_qt_widget_lifecycle(qtbot) -> None:
    widget = QWidget()
    label = QLabel("S08 Qt smoke", parent=widget)
    qtbot.addWidget(widget)

    widget.show()
    assert widget.isVisible()
    assert label.text() == "S08 Qt smoke"

    widget.close()
    assert not widget.isVisible()
