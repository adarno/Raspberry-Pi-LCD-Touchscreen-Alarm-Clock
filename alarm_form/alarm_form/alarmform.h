#ifndef ALARMFORM_H
#define ALARMFORM_H

#include <QMainWindow>

namespace Ui {
class AlarmForm;
}

class AlarmForm : public QMainWindow
{
    Q_OBJECT

public:
    explicit AlarmForm(QWidget *parent = 0);
    ~AlarmForm();

private:
    Ui::AlarmForm *ui;
};

#endif // ALARMFORM_H
