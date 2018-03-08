#include "alarmform.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    AlarmForm w;
    w.show();

    return a.exec();
}
