#ifndef ALARM_WINDOW_H
#define ALARM_WINDOW_H

#include <QDialog>

namespace Ui {
class Alarm_window;
}

class Alarm_window : public QDialog
{
    Q_OBJECT

public:
    explicit Alarm_window(QWidget *parent = 0);
    ~Alarm_window();

private:
    Ui::Alarm_window *ui;
};

#endif // ALARM_WINDOW_H
