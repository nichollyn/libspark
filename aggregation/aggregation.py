from PySide.QtCore import QObject, \
    QReadLocker, QWriteLocker, QReadWriteLock, \
    qWarning, \
    Signal, Slot


KDEBUG = False


class Aggregate(QObject):
    changed = Signal()

    @staticmethod
    def __aggregate_map():
        if not hasattr(Aggregate.__aggregate_map, "map"):
            Aggregate.__aggregate_map.map = {}

        return Aggregate.__aggregate_map.map

    @staticmethod
    def lock():
        if not hasattr(Aggregate.lock, "rwlock"):
            Aggregate.lock.rwlock = QReadWriteLock()
        return Aggregate.lock.rwlock

    @staticmethod
    def parent_aggregate(obj):
        QReadLocker(Aggregate.lock())
        return Aggregate.__aggregate_map().get(obj)

    @Slot()
    def __delete_self(self, obj):
        QWriteLocker(Aggregate.lock())
        del Aggregate.__aggregate_map()[obj]
        del self.__components[:]

    def add(self, component):
        if component is None:
            return

        QWriteLocker(Aggregate.lock())
        parent_aggregation = Aggregate.__aggregate_map().get(component)
        if parent_aggregation == self:
            return

        if parent_aggregation is not None:
            qWarning("Cannot add a component that belongs to a different aggregate: "
                     + str(component))
            return

        self.__components.append(component)
        component.destroyed.connect(self.__delete_self)
        Aggregate.__aggregate_map()[component] = self
        # K DEBUG
        if KDEBUG:
            print("parent aggregate map add component: " + component.objectName())
        #

        self.changed.emit()

    def remove(self, component):
        if component is None:
            return

        QWriteLocker(Aggregate.lock())
        del Aggregate.__aggregate_map()[component]
        del self.__components[:]
        component.destroyed.disconnect(self.__delete_self)

        self.emit(self.changed)

    def component(self, classinfo):
        QReadLocker(Aggregate.lock())
        for component in self.__components:
            if isinstance(component, classinfo):
                return component

        return None

    def components(self, classinfo):
        QReadLocker(Aggregate.lock())
        result = []
        for component in self.__components:
            if isinstance(component, classinfo):
                result.append(component)

        return result

    def __init__(self, parent=None):
        super(Aggregate, self).__init__(parent)

        self.__components = []

        QWriteLocker(Aggregate.lock())
        Aggregate.__aggregate_map()[self] = self


def _query(aggregate, classinfo):
    if aggregate is None:
        return None

    return aggregate.component(classinfo)


def query(obj, classinfo):
    if obj is None:
        return None

    if isinstance(obj, classinfo):
        return obj
    else:
        QReadLocker(Aggregate.lock())
        parent_aggregation = Aggregate.parent_aggregate(obj)
        if parent_aggregation is not None:
            return _query(parent_aggregation, classinfo)
        else:
            return None


def _query_all(aggregate, classinfo):
    if aggregate is None:
        return []

    return aggregate.components(classinfo)


def query_all(obj, classinfo):
    if object is None:
        return []

    QReadLocker(Aggregate.lock())
    parent_aggregation = Aggregate.parent_aggregate(obj)
    results = []
    if parent_aggregation is not None:
        results = _query_all(parent_aggregation, classinfo)
    elif isinstance(obj, classinfo):
        results.append(obj)

    return results
