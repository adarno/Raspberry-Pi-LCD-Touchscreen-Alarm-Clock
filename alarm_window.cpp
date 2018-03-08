#include "alarm_window.h"
#include "ui_alarm_window.h"

Alarm_window::Alarm_window(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::Alarm_window)
{
    ui->setupUi(this);
}

Alarm_window::~Alarm_window()
{
    delete ui;
}
